Deploy to Openshift
===================

This is a wallk through of deploying and Ansible Container example app to Openshift Online (Next Gen) Developer Preview.



ansible-container push --url http://registry.dev-preview-stg.openshift.com/ --namespace example

ansible-container shipit openshift --url http://registry.dev-preview-stg.openshift.com --namespace example