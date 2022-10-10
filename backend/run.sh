#!/bin/bash

uvicorn main:app --workers 8 --reload
