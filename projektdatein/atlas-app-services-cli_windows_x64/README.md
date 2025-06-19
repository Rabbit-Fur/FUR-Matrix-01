# Atlas App Services CLI

## Installation

### NPM

```cmd
npm install -g atlas-app-services-cli
```

## Setup

See detailed instructions on the [MongoDB Atlas App Services Documentation](https://www.mongodb.com/docs/atlas/app-services/cli/)

## Overview

The `appservices` CLI helps manage your Atlas App Services application's changes via your local machine.

An application is structured in your filesystem as a collection of directories and files corresponding configurable entities that can be set up for your application.

See the [App Configuration documentation](https://www.mongodb.com/docs/atlas/app-services/reference/config/#app-configuration) for more details.

## Quick Start

### Logging In
```bash
appservices login
```
This command will bring you to the Access Manager page in Atlas, where you can create an API key and set permissions.  Once you have done that be sure to copy the public and private key and fill out the interactive prompts in the CLI.

### Creating a "blank slate" application

```bash
appservices app create  --name <your app name>
```

When not all required parameters are supplied, the CLI will prompt you to provide the necessary information

**Default Options**

The CLI will create an app using sensible defaults for any parameter that is not required and not supplied

- [--deployment-model](https://www.mongodb.com/docs/atlas/app-services/apps/deployment-models-and-regions/#deployment-models): `GLOBAL`
- [--provider-region](https://www.mongodb.com/docs/atlas/app-services/apps/deployment-models-and-regions/#cloud-deployment-regions): `aws-us-east-1`


### Creating a template starter application

You can generate a fully working application in the language of your choice in a single command using template starter applications.

To use them to create apps in the CLI you can supply `--template` to the `app create` command.

A full list of template apps are documented [here](https://www.mongodb.com/docs/atlas/app-services/reference/template-apps/#template-apps-available)

**Note that template apps require a provisioned atlas cluster to create

ie:

```bash
appservices create --name myApp --template sync.todo --cluster myCluster1
```

## App Services Application Development Tips + Best Practices

1. Use `git` to track changes to your application over time. This is especially useful for working in teams.
    - See [Automatic Deployments](https://www.mongodb.com/docs/atlas/app-services/apps/#automate-deployment) for a built-in way to sync changes to your application with `git`
2. You can test your functions in the CLI using the `appservices function run` command.