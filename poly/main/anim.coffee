###
# Define a basic animations library; useful for loading and transitions.
###
ANIMATIONS =
  loading:
    interval: 200,
    frames: [
      'anim_loading_0.svg',
      'anim_loading_1.svg',
      'anim_loading_2.svg'
    ]

class Animation
  constructor: (animName, container) ->
    anim = ANIMATIONS[animName]
    if !anim
      throw "Animation " + animName + " does not exist!"

    @div = div = $("<DIV>")
    div.addClass("anim")
    div.addClass(animName)
    $(container).append(div)

    _.defer () ->
      div.css
        width: div.height()
        marginLeft: -div.height()/2
        marginTop: -div.height()/2

    images = _.map anim.frames, (src) =>
      img = new Image()
      img.src = '/static/main/images/' + src
      img

    curFrame = 0
    advFrame = () ->
      div.css 'background-image', 'url(' + images[curFrame].src + ')'
      curFrame = (curFrame + 1) % images.length
    @interval = setInterval advFrame, anim.interval

  remove: () =>
    @div.remove()
    clearInterval @interval

  stopOnImage: (imgSrc) =>
    @div.css 'background-image', 'url(' + imgSrc + ')'
    clearInterval @interval

module.exports = Animation
