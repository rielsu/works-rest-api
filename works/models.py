from django.db import models
from django_pgviews import view as pg

class Work(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    iswc = models.CharField(max_length=20)

class Contributor(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

class Source(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    source_id = models.IntegerField()
    status = models.CharField(max_length=50)

class WorksView(pg.View):
    projection = ['works.Work.title','works.Contributor.name','works.Work.iswc']
    sql = """SELECT w.id id,w.title title, string_agg(c.name, '|') contributors, w.iswc iswc FROM works_work AS w
        INNER JOIN works_contributor AS c ON w.id = c.work_id
        GROUP BY w.iswc,w.title,w.id"""
    class Meta:
        db_table = 'works_single_view'
        managed = False


