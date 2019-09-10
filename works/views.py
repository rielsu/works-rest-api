 
from rest_framework.response import Response
from .models import WorksView, Work
from rest_framework.views import APIView
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from .processing import worksManager
from .models import Work
from django.http import HttpResponse 
from django.db import models, connection, transaction
import csv
cursor = connection.cursor()


class WorkView(APIView):
    def post(self, request, format=None):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="works_metadata.csv"'
        writer = csv.writer(response)
        writer.writerow(['Title', 'Contributors', 'ISWC'])
        iswcList = request.data['iswc']
        for iswc in iswcList:
            workRaw = Work.objects.raw("SELECT * FROM works_single_view WHERE iswc = '{}';".format(iswc))
            work =workRaw[0]
            writer.writerow([work.title, work.contributors, work.iswc])
        return response


class FileUploadView(APIView):
    parser_classes = (MultiPartParser,)
    def post(self, request, format=None):
        file = request.data['file']
        response = worksManager(file)
        return Response({'recieved data': response})


