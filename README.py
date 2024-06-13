# Databricks notebook source
API_ROOT = (
    dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()
)
API_TOKEN = (
    dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
)
