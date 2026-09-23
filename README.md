Las claves para el acceso son:


Usuario: rrhh_user
Contraseña: supersecret


Se tuvieron problemas para que la api funcione correctamente, debido a que no me reconoce el puerto 


PS C:\6toSEM\Emergentes_1\rrhhmarc-jguevara> curl.exe -X POST http://localhost:5000/api/marcaciones -H "Content-Type: application/json" -d "{\"codigo_empleado\":\"EMP001\",\"nombre_empleado\":\"Ana Perez\",\"fecha\":\"2026-09-23\",\"hora_ingreso_programada\":\"08:00\",\"hora_ingreso_real\":\"08:12\",\"hora_salida_programada\":\"16:00\",\"hora_salida_real\":\"16:05\"}"
curl: (7) Failed to connect to localhost:5000 after 2219 ms: Could not connect to server
curl: (3) URL rejected: Port number was not a decimal number between 0 and 65535
curl: (3) URL rejected: Port number was not a decimal number between 0 and 65535
PS C:\6toSEM\Emergentes_1\rrhhmarc-jguevara> 
PS C:\6toSEM\Emergentes_1\rrhhmarc-jguevara> curl http://localhost:5000/api/marcaciones
curl : No es posible conectar con el servidor remoto
En línea: 1 Carácter: 1
+ curl http://localhost:5000/api/marcaciones
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : InvalidOperation: (System.Net.HttpWebRequest:HttpWebRe 
   quest) [Invoke-WebRequest], WebException
    + FullyQualifiedErrorId : WebCmdletWebResponseException,Microsoft.PowerShell.Com 
   mands.InvokeWebRequestCommand
 
PS C:\6toSEM\Emergentes_1\rrhhmarc-jguevara> 
