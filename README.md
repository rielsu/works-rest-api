# works-rest-api
## REST API to music works

### to Start:
  docker-compose up
  
### To Shutdown:
  docker-compose down
  

EndPoints

0.0.0.0:8000/api/upload
```
  *Header Content-Type => multipart/form-data 
  *.csv File with a format of 
        title,contributors,iswc,source,id
        'BLOW','Ed Sheeran|Bruno Mars|Cris Stapleton','T0046951705',warner,129
  *return Sucess Message if the process was Succesfull
 ```

0.0.0.0:8000/api/works
```
  *input Content-Type => application/json
  * list of iswc 
          example of body
          {
            iswc: ['T0046951705','T0046951706']
          }
          
  *returns .csv File with metadata information 
        title,contributors,iswc
        'BLOW','Ed Sheeran|Bruno Mars|Cris Stapleton','T0046951705'
