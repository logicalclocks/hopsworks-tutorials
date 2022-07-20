<div style="text-align:center">
<img src="images/heroku.jpg">
</div>

# <span style="color:#ff5f27;">⚪️🟣 🚀 Deploying project using Heroku</span>

### <span style="color:#ff5f27;">🤔 What is Heroku?</span>
---

Heroku is a cloud platform that lets you build, deliver, monitor and scale apps.

It is a way to run your script rather than executing the script from your local machine.

### <span style="color:#ff5f27;">🔬 🧬 Project Creation</span>
---
First of all we need to prepare our project for Heroku.

It should have 3 specific files besides your Python script:

- **Procfile**
- **Requirements.txt**
- **Runtime.txt**

#### <span style="color:#ff5f27;">⛳️ Procfile</span>
In this file we specify the name of a main script which Heroku should run.

![](images/heroku_img1.png)

#### <span style="color:#ff5f27;">⛳️ Requirements.txt</span>

In this file we specify the correct versions of the required Python libraries to run your Python code.

![](images/heroku_img2.png)

#### <span style="color:#ff5f27;">⛳️ Runtime.txt</span>

In this file we can define our Python (or other languages) version that we are going to use in our project.

![](images/heroku_img3.png)

## <span style="color:#ff5f27;">🪄 Heroku Setup</span>

1. Create Heroku account. (https://signup.heroku.com/login).
2. Install the Heroku CLI on your Computer (https://devcenter.heroku.com/articles/heroku-cli).

## <span style="color:#ff5f27;">📝 Api Keys Preparation</span>

You can securely save Api Keys using Heroku UI and then easily access them in code.

![](images/api_keys1.png)

![](images/api_keys2.png)

## <span style="color:#ff5f27;"> 🚀 Deploying to Heroku</span>

Now, it is time to deploy our project to Heroku.

Open project folder on Command Line Interface (CLI). Inside your environment use the following commands:


- `heroku login`

- `heroku create YOUR_APP_NAME`

- `git init`

- `git add .`

- `git commit -m "Great commit"`

- `git push heroku master `


To display an output of project - use next command:

- `heroku logs -t -s app -a YOUR_APP_NAME`

---

### <span style="color:#ff5f27;">🕵🏻‍♂️ If you don't see any output check if worker is turned on</span>

![](images/heroku_img4.png)

---
