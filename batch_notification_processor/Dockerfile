FROM public.ecr.aws/lambda/python:3.12

COPY --from=root_dir Pipfile ${LAMBDA_TASK_ROOT}
COPY --from=root_dir Pipfile.lock ${LAMBDA_TASK_ROOT}
COPY *.py ${LAMBDA_TASK_ROOT}

RUN pip install pipenv
RUN pipenv install --system

CMD [ "lambda_function.lambda_handler" ]
