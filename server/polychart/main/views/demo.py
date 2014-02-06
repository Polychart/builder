"""
Django handlers to deal with the demo.
"""
import json

from django.shortcuts             import render
from django.views.decorators.http import require_GET, require_http_methods

from polychart.main.models import TutorialCompletion

@require_GET
def demoShow(request):
  """Django handler to show the demo dashboard."""
  # pylint: disable = E1101
  # Pylint does not recognize Django model attributes.
  if request.user.is_authenticated():
    showTutorial = not TutorialCompletion.objects.filter(user=request.user, type='nux').exists()
  else:
    showTutorial = True

  tutorialOverride = request.GET.get('showTutorial', None)
  if tutorialOverride == 'yes':
    showTutorial = True
  elif tutorialOverride == 'no':
    showTutorial = False

  return render( request
               , 'demo.tmpl'
               , dictionary = { 'showTutorial': showTutorial })

