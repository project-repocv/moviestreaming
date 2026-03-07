pipeline {
    agent any

    environment {
        // Branch mappings
        DEV_BRANCH = 'develop'
        STAGING_BRANCH_PREFIX = 'release/'
        PROD_BRANCH = 'main'

        // AWS / ECR
        AWS_ACCOUNT_ID = '781863585922'
        AWS_DEFAULT_REGION = 'us-east-1'
        ECR_REGISTRY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com"

        // Docker tagging
        COMMIT_HASH = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
        BRANCH_NAME_TAG = "${env.BRANCH_NAME}".replaceAll('/', '-')
        IMAGE_TAG = "${BRANCH_NAME_TAG}-${COMMIT_HASH}"

        SONAR_HOST_URL = 'http://<sonarqube-ip>:9000'
    }

    stages {

        // --------------------------------------------------------------
        // 1. Branch validation – only proceed for develop, release/*, main
        // --------------------------------------------------------------
        stage('Check Allowed Branch') {
            steps {
                script {
                    def allowed = false
                    if (env.BRANCH_NAME == env.DEV_BRANCH ||
                        env.BRANCH_NAME.startsWith(env.STAGING_BRANCH_PREFIX) ||
                        env.BRANCH_NAME == env.PROD_BRANCH) {
                        allowed = true
                    }
                    env.ALLOWED_BRANCH = allowed.toString()
                    echo "Branch '${env.BRANCH_NAME}' allowed? ${env.ALLOWED_BRANCH}"
                    if (!allowed) {
                        currentBuild.result = 'SUCCESS'
                        echo "Branch '${env.BRANCH_NAME}' is not a build branch. Pipeline finished."
                    }
                }
            }
        }

        stage('Checkout') {
            when { expression { env.ALLOWED_BRANCH == 'true' } }
            steps {
                checkout scm
            }
        }

        stage('Detect Environment') {
            when { expression { env.ALLOWED_BRANCH == 'true' } }
            steps {
                script {
                    if (env.BRANCH_NAME == env.DEV_BRANCH) {
                        env.TARGET_ENV = 'dev'
                        env.DEPLOY_STRATEGY = 'auto'
                    } else if (env.BRANCH_NAME.startsWith(env.STAGING_BRANCH_PREFIX)) {
                        env.TARGET_ENV = 'staging'
                        env.DEPLOY_STRATEGY = 'manual'
                    } else if (env.BRANCH_NAME == env.PROD_BRANCH) {
                        env.TARGET_ENV = 'prod'
                        env.DEPLOY_STRATEGY = 'manual'
                    } else {
                        // Should never happen due to branch filter, but keep for safety
                        env.TARGET_ENV = 'unknown'
                        env.DEPLOY_STRATEGY = 'none'
                    }

                    echo "Target environment: ${env.TARGET_ENV}"
                }
            }
        }

        // /* ======================================================
        //    TERRAFORM APPLY (REMOTE BACKEND: S3 + DYNAMODB)
        // ======================================================= */
        // stage('Terraform Infrastructure Apply') {
        //     when {
        //         expression { env.TARGET_ENV != 'feature' && env.ALLOWED_BRANCH == 'true' }
        //     }
        //     steps {
        //         dir("cinevision-infrastructure/environments/${env.TARGET_ENV}") {
        //             withCredentials([aws(credentialsId: 'aws-credentials')]) {
        //                 sh '''
        //                     echo "Initializing Terraform with remote backend..."
        //                     terraform init -reconfigure

        //                     echo "Validating configuration..."
        //                     terraform validate

        //                     echo "Planning infrastructure..."
        //                     terraform plan -out=tfplan

        //                     echo "Applying infrastructure..."
        //                     terraform apply -auto-approve tfplan
        //                 '''
        //             } 
        //         }
        //     }
        // }

        // /* ======================================================
        //    TERRAFORM DESTROY (DEV ONLY - IMMEDIATE AFTER APPLY)
        // ======================================================= */
        // stage('Terraform Destroy (Dev Only)') {
        //     when {
        //         allOf {
        //             expression { env.BRANCH_NAME == env.DEV_BRANCH }
        //             expression { env.TARGET_ENV == 'dev' }
        //             expression { env.ALLOWED_BRANCH == 'true' }
        //         }
        //     }
        //     steps {
        //         dir("cinevision-infrastructure/environments/dev") {
        //             withCredentials([aws(credentialsId: 'aws-credentials')]) {
        //                 sh '''
        //                     echo "Re-initializing Terraform..."
        //                     terraform init -reconfigure

        //                     echo "Destroying Dev infrastructure..."
        //                     terraform destroy -auto-approve
        //                 '''
        //             }
        //         }
        //     }
        // }

        /* =======================================================
           INSTALL PARENT POM (now under /backend)
        ======================================================= */
        stage('Install Parent POM') {
            when {
                expression { env.TARGET_ENV != 'feature' && env.ALLOWED_BRANCH == 'true' }
            }
            steps {
                dir('backend') {
                    // Install the parent POM without building modules
                    sh 'mvn clean install -N'
                }
            }
        }

        stage('Check Java Version') {
            when { expression { env.ALLOWED_BRANCH == 'true' } }
            steps {
                sh 'java -version'
                sh 'javac -version'
            }
        }

        /* ======================================================
           BUILD & TEST MICROSERVICES
           Backend services are under /backend/<service>
           Frontend is under /frontend
        ======================================================= */
        stage('Build & Test Services') {
            when { expression { env.ALLOWED_BRANCH == 'true' } }
            parallel {

                stage('API Gateway') {
                    steps {
                        dir('backend/api-gateway') {
                            sh 'mvn clean package'
                        }
                    }
                }

                stage('Movie Service') {
                    steps {
                        dir('backend/movieService') {
                            sh 'mvn clean package'
                        }
                    }
                }

                stage('User Service') {
                    steps {
                        dir('backend/userService') {
                            sh 'mvn clean package'
                        }
                    }
                }

                stage('Email Service') {
                    steps {
                        dir('backend/emailService') {
                            sh 'mvn clean package'
                        }
                    }
                }

                stage('Eureka Server') {
                    steps {
                        dir('backend/eureka-server') {
                            sh 'mvn clean package'
                        }
                    }
                }

                stage('Frontend (React)') {
                    agent {
                        docker {
                            image 'node:20'
                            args '-u root'
                        }
                    }
                    steps {
                        script {
                            catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                                dir('frontend') {
                                    sh '''
                                        npm ci
                                        CI=false npm run build
                                    '''
                                }
                            }
                        }
                    }
                }
            }
        }

        // /* =======================================================
        //    SONARQUBE ANALYSIS (only backend services)
        // ========================================================= */
        // stage('SonarQube Analysis') {
        //     when {
        //         expression { env.TARGET_ENV != 'feature' && env.ALLOWED_BRANCH == 'true' }
        //     }
        //     steps {
        //         withSonarQubeEnv('SonarQube') {
        //             script {
        //                 def backendServices = [
        //                     'api-gateway',
        //                     'movieService',
        //                     'userService',
        //                     'emailService',
        //                     'eureka-server'
        //                 ]
        //                 backendServices.each { service ->
        //                     dir("backend/${service}") {
        //                         sh 'mvn sonar:sonar'
        //                     }
        //                 }
        //             }
        //         } 
        //     }
        // }

        // stage('Quality Gate') {
        //     when {
        //         expression { env.TARGET_ENV != 'feature' && env.ALLOWED_BRANCH == 'true' }
        //     }
        //     steps {
        //         timeout(time: 1, unit: 'HOURS') {
        //             waitForQualityGate abortPipeline: true
        //         }
        //     }
        // }

        /* =======================================================
           BUILD & PUSH DOCKER IMAGES
           Each service's Dockerfile is inside its own directory
        ======================================================= */
        stage('Build & Push Docker Images') {
            when {
                expression { env.TARGET_ENV != 'feature' && env.ALLOWED_BRANCH == 'true' }
            }
            steps {
                withAWS(region: "${AWS_DEFAULT_REGION}", credentials: 'aws-credentials') {
                    script {
                        sh """
                            aws ecr get-login-password --region ${AWS_DEFAULT_REGION} \
                            | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                        """

                        def backendServices = [
                            'api-gateway',
                            'movieService',
                            'userService',
                            'emailService',
                            'eureka-server'
                        ]
                        def frontendServices = ['frontend']

                        // Build and push backend services
                        backendServices.each { service ->
                            dir("backend/${service}") {
                                def lowerService = service.toLowerCase()
                                def imageName = "${ECR_REGISTRY}/cinevision/${lowerService}:${IMAGE_TAG}"

                                sh "docker build -t ${imageName} ."
                                sh "docker push ${imageName}"

                                sh "docker tag ${imageName} ${ECR_REGISTRY}/cinevision/${lowerService}:latest"
                                sh "docker push ${ECR_REGISTRY}/cinevision/${lowerService}:latest"
                            }
                        }

                        // Build and push frontend
                        frontendServices.each { service ->
                            dir('frontend') {
                                def lowerService = service.toLowerCase()
                                def imageName = "${ECR_REGISTRY}/cinevision/${lowerService}:${IMAGE_TAG}"

                                sh "docker build -t ${imageName} ."
                                sh "docker push ${imageName}"

                                sh "docker tag ${imageName} ${ECR_REGISTRY}/cinevision/${lowerService}:latest"
                                sh "docker push ${ECR_REGISTRY}/cinevision/${lowerService}:latest"
                            }
                        }
                    }
                }
            }

        }

        /* ========================================================
           DELETE IMAGES AFTER PUSH TO ECR (commented out)
        ======================================================= */
        // stage('Delete Images from ECR (DANGER)') {
        //     when { expression { env.TARGET_ENV == 'dev' && env.ALLOWED_BRANCH == 'true' } }
        //     steps {
        //         withAWS(region: AWS_DEFAULT_REGION, credentials: 'aws-credentials') {
        //             script {
        //                 def services = ['api-gateway','movieService','userService','emailService','eureka-server','frontend']
        //                 services.each { service ->
        //                     def repoName = service.toLowerCase()
        //                     sh """
        //                         aws ecr batch-delete-image \
        //                         --repository-name cinevision/${repoName} \
        //                         --image-ids imageTag=${IMAGE_TAG} imageTag=latest \
        //                         --region ${AWS_DEFAULT_REGION} || true
        //                     """
        //                 }
        //             }
        //         }
        //     }
        // }

        /* ======================================================
           MANUAL APPROVAL (STAGING & PROD)
        ======================================================= */
        stage('Manual Approval') {
            when {
                expression { env.DEPLOY_STRATEGY == 'manual' && env.ALLOWED_BRANCH == 'true' }
            }
            steps {
                input message: "Approve deployment to ${env.TARGET_ENV}?",
                    ok: 'Deploy'
            }
        }

        /* ======================================================
           DEPLOY TO KUBERNETES
           (k8s manifests remain at root /k8s)
        ======================================================== */
        stage('Deploy to Kubernetes') {
            when {
                expression { env.TARGET_ENV != 'feature' && env.ALLOWED_BRANCH == 'true' }
            }
            steps {
                dir("k8s/${env.TARGET_ENV}") {

                    
                    withAWS(credentials: 'aws-credentials', region: 'us-east-1') {
                        withKubeConfig(credentialsId: 'kubeconfig') {
                            script {

                                // 1. Ensure the namespace exists
                                sh "kubectl create namespace cinevision-${TARGET_ENV} --dry-run=client -o yaml | kubectl apply -f -"

                                // 2. Apply all Kubernetes manifests from the current directory
                                sh "kubectl apply -f . -n cinevision-${TARGET_ENV}"


                                def services = [

                                    'movieService',
                                    'api-gateway',
                                    'userService',
                                    'emailService',
                                    'eureka-server',
                                    'frontend'
                                ]
                                services.each { service ->
                                    def lowerService = service.toLowerCase()

                                    sh """
                                        kubectl set image deployment/${lowerService} \
                                        ${lowerService}=${ECR_REGISTRY}/cinevision/${lowerService}:${IMAGE_TAG} \
                                        -n cinevision-${TARGET_ENV} --record
                                    """
                                }
                                sh "kubectl rollout status deployment -n cinevision-${TARGET_ENV}"
                            }
                        }
                    }    
                }   
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo "Pipeline completed successfully for ${env.BRANCH_NAME}"
        }
        failure {
            echo "Pipeline failed for ${env.BRANCH_NAME}"
        }
    }
}