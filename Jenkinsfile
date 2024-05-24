#!/usr/bin/env groovy
pipeline {
  agent {
      label 'commonagent'
  }

  stages {
    stage('Build docker container') {
      steps {
        ansiColor('xterm') {
        	sh('docker build -t cip-insights-reputation/companies-house-download-lambda .')
        }
      }
    }
    stage('Push to ecr') {
      steps {
        script {
          build_version = readFile ".version"
        }
        sh("""
          aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 727065427295.dkr.ecr.eu-west-2.amazonaws.com
          docker tag cip-insights-reputation/companies-house-download-lambda:latest 727065427295.dkr.ecr.eu-west-2.amazonaws.com/cip-insights-reputation/companies-house-download-lambda:$build_version
          docker push 727065427295.dkr.ecr.eu-west-2.amazonaws.com/cip-insights-reputation/companies-house-download-lambda:$build_version
        """)
      }
    }
  }
}
