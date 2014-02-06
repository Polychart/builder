Events = require('poly/main/events')

init = () ->
  Events.signup.page.view.trigger()
  eulaClickTrap '#start', '#realsubmit', '#eula', Events.signup.eula.error
  Events.signup.form.submit.trackForm $('#realsubmit')
  $('input').on 'keypress keydown', _.once ->
    Events.signup.form.interact.trigger()

eulaClickTrap = (submitBtn, hiddenBtn, eula, errorEvt) ->
  $(submitBtn).on 'click', (e) ->
    e.stopPropagation()
    if $(eula).prop 'checked'
      $(hiddenBtn).click()
    else
      if errorEvt then errorEvt.trigger()
      alert 'You must first read and accept the Terms and Conditions.'

module.exports = {
  init
}
