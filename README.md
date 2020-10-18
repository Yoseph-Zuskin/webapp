<h1 align="center"><a href="https://bankofcanada.herokuapp.com/">Bank of Canada Open Data Explorer</a></h1>

<h2 align="center">Streamlit Web Application Documentation</h2>

<p align="center">
<img alt="Project Logo" src="project_logo.png">
</p>

<p align="center">
<a href="https://github.com/Yoseph-Zuskin/webapp/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/Yoseph-Zuskin/webapp"></a>
<a href="https://github.com/Yoseph-Zuskin/webapp/network"><img alt="GitHub forks" src="https://img.shields.io/github/forks/Yoseph-Zuskin/webapp"></a>
<a href="https://github.com/Yoseph-Zuskin/webapp/stargazers"><img alt="Github Stars" src="https://img.shields.io/github/stars/Yoseph-Zuskin/webapp"></a>
<a href="https://github.com/Yoseph-Zuskin/webapp/blob/main/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/Yoseph-Zuskin/webapp"></a>
<a href="https://github.com/Yoseph-Zuskin/webapp/"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

## Contents

1. [Introduction](#section01)
    - [Features](#section01a)
3. [Project Details](#section02)
    - [Demonstration](#section02a)
    - [Repository Details](#section02b)
    - [Forecasting](#section02c)
4. [License](#section03)


<a id='section01'></a>

## Introduction

This web application was developed as a front-end GUI for the [PyValet API](https://github.com/tylercroberts/pyvalet).
The API provides free access to the economic open data which the Bank of Canada makse available to the public.
Please :memo: [report any issues](https://github.com/Yoseph-Zuskin/webapp/issues) that you encounter, and on the top right,
you can :eyes: watch for new updates, :star: hit start to show your support, or :file_folder: create a fork of this report
and play around with the code on your own. :pray: Thank you for your interest in this web application!

<a id='section01a'></a>

### Features of this web application

* **Data Selection:** Users may select multiple time series from the same data group, which they can also choose.

* **Data Exploration:** Users may view the tabular data, interact with a plot of the data, and download it as a CSV file.

* **Data Forecasting (COMING SOON):** Users will soon be able to generate a forecasting pipeline and export the files needed to run it locally

<a id='section02'></a>

## Project Details

<a id='section02a'></a>

### Demonstration

<p align="center">
<img alt="Demo" src="demo.gif">
</p>

<a id='section02b'></a>

### Repository Details

This repository contains the Python code for the Bank of Canada Open Data Explorer web application, as well as some accompanying
Schell script and Procfile used by [Heroku]('https://www.heroku.com/') to spin up the website upon deployment. Below are the main
files which are used to orchestrate this web application:

    .
    ├── src
    │   ├── main.py
    │   └── custom.py
    ├── Procfile
    ├── requirements.txt
    ├── setup.sh
    └── ...

The other files contained within this repository include the license, readme file, and images used within the readme file

<a id='section02c'></a>

### COMING SOON: Time Series Forecasting

Currently under development is another feature to this web application which will enable easy time series forecasting.
The plan is to initially begin with the [Auto-ARIMA](http://alkaline-ml.com/pmdarima/#) and [Facebook Prophet]()
models, and enable users to not only create their own models on this web application, but also export a Python script
or IPython notebook that will let users work with the models they create on local or cloud environments of their choosing,
so long as they have Python 3 and the dependencies listed in the `requirements.txt` file installed.

<a id='section03'></a>

## License

This project is licensed under the GPL-3.0 License - please see the [LICENSE](https://github.com/Yoseph-Zuskin/webapp/blob/main/LICENSE) file for details