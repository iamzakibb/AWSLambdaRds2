def installTerraform() {
    // Check if terraform is already installed
    def terraformExists = sh(script: 'which terraform', returnStatus: true)
    if (terraformExists != 0) {
        // Install terraform
        sh '''
            echo "Installing Terraform..."
            wget https://releases.hashicorp.com/terraform/1.0.0/terraform_1.0.0_linux_amd64.zip
            unzip terraform_1.0.0_linux_amd64.zip
            sudo mv terraform /usr/local/bin/
            rm -f terraform_1.0.0_linux_amd64.zip
        '''
    } else {
        echo "Terraform already installed!"
    }
}

pipeline {

    parameters {
        string(name: 'environment', defaultValue: 'terraform', description: 'Workspace/environment file to use for deployment')
        booleanParam(name: 'autoApprove', defaultValue: false, description: 'Automatically run apply after generating plan?')

    }

    environment {
        AWS_ACCESS_KEY_ID     = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
    }

    agent any

    stages {
        stage('Initial') {
            steps {
                sh '''
                   echo "Hey"
                '''
            }
        }

        stage('checkout') {
            steps {
                script {
                    git "https://github.com/iamzakibb/AWSLambdaRds2.git"
                }
            }
        }

        stage('Plan') {
            steps {
                sh 'pwd; terraform init -input=false'
                sh 'pwd; terraform workspace new ${environment}'
                sh 'pwd; terraform workspace select ${environment}'
                sh "pwd; terraform plan -input=false -out tfplan "
                sh 'pwd; terraform show -no-color tfplan > tfplan.txt'
            }
        }

        stage('Approval') {
            when {
                not {
                    equals expected: true, actual: params.autoApprove
                }
            }

            steps {
                script {
                    def plan = readFile 'tfplan.txt'
                    input message: "Do you want to apply the plan?",
                          parameters: [text(name: 'Plan', description: 'Please review the plan', defaultValue: plan)]
                }
            }
        }

        stage('Apply') {
            steps {
                sh 'terraform apply -input=false tfplan'
            }
        }
    }

}
