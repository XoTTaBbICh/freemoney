from yandex_money import api

print(api.Wallet.build_obtain_token_url(client_id='103703A821D04244A16FA4554553725282C76EF2E5491E3690FAC425D7665EB4',redirect_uri='https://37.60.177.245:8443/ya_pay',scope=['account-info', 'operation-history','operation-details'])+'&response_type=code')

# Empty webserver index, return nothing, just http 200


wallet = api.Wallet(access_token='410014484849976.70AF4E00D24F1B514B293E3D49E7B06F90E717BD0576AC40279EDB0EB0C9B3962F2DC031F24449D30E7423AF48041DDFE1B4E154EDA5B442F1406DFBA0B85804C246581D66E7F8ADF39B159322846317A18B643EE950FC5FA739676AAB7D763B077AE2437464BD4D171AE04CAF9852470E31FF36F2745518663E2986B953BE4B')
print(wallet.operation_details(operation_id=512742676385025004))
print(wallet.operation_history({'type':'deposition','details':'true'}))

# app.run(host=settings.WEBHOOK_LISTEN,
#         port=settings.WEBHOOK_PORT,
#         ssl_context=(settings.WEBHOOK_SSL_CERT, settings.WEBHOOK_SSL_PRIV),debug=False)
