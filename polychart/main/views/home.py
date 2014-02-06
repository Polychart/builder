"""
Django handlers to deal with the Dashboard Builder home.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts               import render
from django.views.decorators.http   import require_GET

from polychart.main.models import DataSource, Dashboard, TutorialCompletion

@require_GET
@login_required
def show(request):
  """Django handler to render home."""
  # pylint: disable = E1101
  # Pylint does not notice Django model attributes
  newDataSourceKey = request.GET.get('newDataSourceKey', None)

  dataSources       = DataSource.objects.filter(user=request.user)
  dashboards        = Dashboard.objects.filter(user=request.user)
  tutorialCompleted = TutorialCompletion.objects.filter(user=request.user, type='nux').exists()

  return render( request
               , 'home.tmpl'
               , dictionary = { 'dataSources':       dataSources
                              , 'dashboards':        dashboards
                              , 'tutorialCompleted': tutorialCompleted
                              , 'newDataSourceKey':  newDataSourceKey })
