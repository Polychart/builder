"""
Django handlers related to the tutorial.
"""
import json

from django.contrib.auth.decorators import login_required
from django.views.decorators.http   import require_POST

from polychart.main.models import TutorialCompletion
from polychart.utils       import jsonResponse

@require_POST
@login_required
def tutorialComplete(request):
  """Django handler for completion of the tutorial."""
  body = json.loads(request.body)

  TutorialCompletion(
    user=request.user,
    type=body['type']
  ).save()

  return jsonResponse({})
