from fastapi import Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

def http_error(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder({'message': exc.detail}),
    )

def validation_error(request: Request, exc: RequestValidationError):
    #import pdb; pdb.set_trace()
    message, data = resolve_exception_message(exc)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({'message': message, 'data': data}),
    )

def resolve_exception_message(exc: RequestValidationError):
    data = []
    for error in exc.errors():
        error_data = {'field': error['loc'][1]}
        # hack to check if the validation message text is custom
        if error['type'] == 'value_error.customvalidationexception':
            error_data['message'] = error['msg']
        else:
            # process internal validation messages
            error_data['message'] = f"{error['msg']} for {error['loc'][1]}.".capitalize()
        data.append(error_data)
    return data[0]['message'], data
