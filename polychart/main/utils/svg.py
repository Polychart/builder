"""
Functions to construct SVG from a serialized dashboard state.
"""
import svgwrite
import re

from sys import float_info
from os  import tmpfile

from polychart.main.utils.colours import getHex

EPSILON         = float_info.epsilon
COMMENT_PADDING = 10
AUTHOR_PADDING  = 8
AUTHOR_HEIGHT   = 12
GRID_SIZE       = 25
JS_ITEMS        = ["ChartItem", "NumeralItem"]

def constructSvg(procSerial):
  """
  Construct a SVG image out of a processed, dashboard builder serialized state.

  Args:
    procSerial: A list representing the dashboard state to be exported. Each item
      in the list is a dictonary with a `itemType` field, detailing what sort of
      item is to be drawn.

      The item types that are drawn so far are 'ChartItem's, 'TitleItem's and
      'CommentItem's.

  Returns:
    A svg string representing the image.
  """
  svgHeight, svgWidth = _getSize(procSerial)
  draw = svgwrite.Drawing(size=(svgWidth, svgHeight))
  drawHead, drawTail  = draw.tostring()[0:-6], draw.tostring()[-6:]
  drawBody = ""
  for dashItem in procSerial:
    position = {k: v * GRID_SIZE for k, v in dashItem['position'].iteritems()}
    w, h, x, y = position['width'], position['height'], position['left'], position['top']
    g = svgwrite.container.Group()
    g.translate(x, ty=y)
    if dashItem['itemType'] in JS_ITEMS:
      for item in dashItem['items']:
        t, attrs = item['type'], item['attr']
        if   t == 'rect':
          svg, attrs = _svgRect(draw, attrs)
        elif t == 'circle':
          svg, attrs = _svgCirc(draw, attrs)
        elif t == 'path':
          svg, attrs = _svgPath(draw, attrs)
        elif t == 'text':
          svg, attrs = _svgText(draw, attrs)
        g.add(svg)

    elif dashItem['itemType'] == 'TitleItem':
      titleSvg, attrs = _svgText(draw,
          { 'x':           0
          , 'y':           0
          , 'text':        dashItem['textContent']
          , 'lineHeight':  dashItem.get('lineHeight', 10)
          , 'font-size':   '1.35em'
          , 'font-family': 'helvetica'
          , 'font-weight': 'bold' })
      g.add(titleSvg)

    elif dashItem['itemType'] == 'CommentItem':
      bgSvg, attrs = _svgRect(draw,
          { 'x':            COMMENT_PADDING
          , 'y':            COMMENT_PADDING
          , 'width':        w - COMMENT_PADDING
          , 'height':       h - COMMENT_PADDING
          , 'fill':         '#fff8b6'
          , 'stroke':       '#eae1a0'
          , 'stroke-width': 1 })
      g.add(bgSvg)

      authorSvg, attrs = _svgText(draw,
          { 'x':           COMMENT_PADDING + AUTHOR_PADDING
          , 'y':           COMMENT_PADDING + 2 * AUTHOR_PADDING
          , 'text':        dashItem['author']
          , 'lineHeight':  dashItem['lineHeight']
          , 'font-weight': 600
          , 'font-size':   '1em'
          , 'fill':        '#8c8c8c'
          , 'clip':        'rect(10,10,{width},{height})'.format(
                             width  = w - COMMENT_PADDING
                           , height = h - COMMENT_PADDING)
          , 'font-family': 'helvetica' })
      g.add(authorSvg)

      textSvg, attrs = _svgText(draw,
          { 'x':           COMMENT_PADDING + AUTHOR_PADDING
          , 'y':           COMMENT_PADDING + AUTHOR_PADDING + AUTHOR_HEIGHT
          , 'text':        dashItem['textContent']
          , 'lineHeight':  dashItem['lineHeight']
          , 'font-weight': 'normal'
          , 'font-size':   '1em'
          , 'font-family': 'helvetica' })
      g.add(textSvg)

    elif dashItem['itemType'] == 'PivotTableItem':
      from weasyprint import HTML, CSS
      dashItem['html'] = dashItem['html']\
        .replace('align="right"', 'class="alignright"')\
        .replace('align="center"', 'class="aligncenter"')
      html = HTML(string=dashItem['html'])

      wpx, hpx = '{width}px'.format(width = w), '{height}px'.format(height = h)
      css = CSS(string="""
        @page {
          margin: 0;
          padding: 0;
          size: %s %s;
        }
        table, th, td, tr {
          border: 1px solid black;
          border-collapse: collapse;
          border-spacing: 0;
          padding: 0;
          margin: 0;
          font-weight: normal;
          background-color: white;
        }
        table {
          width: %s;
          height: %s;
        }
        .alignright {
          text-align: right;
        }
        .aligncenter {
          text-align: center;
        }
      """ % (wpx, hpx, wpx, hpx))

      page = html.render(stylesheets=[css]).pages[0]
      with tmpfile() as tmp:
        import cairocffi as cairo
        surface = cairo.SVGSurface(tmp, x + page.width, y + page.height)
        page.paint(cairo.Context(surface), left_x=x, top_y=y)
        surface.finish()

        tmp.seek(0)
        for line in tmp:
          if re.match(r'<(?:xml|(/)?svg).*>', line) is None:
            drawBody += line
        drawBody = drawBody.rstrip()

    if dashItem['itemType'] != "PivotTableItem":
      drawBody += g.tostring()
  return drawHead + drawBody + drawTail


def _getSize(procSerial):
  """
  Obtain the size of a SVG scene.

  Args:
    procSerial: A processed, dashboard builder serialized state.

  Returns:
    A pair of integers corresponding the (height, width) of the scene.
  """
  height, width = 0, 0
  for item in procSerial:
    position = {key: val * GRID_SIZE for key, val in item['position'].iteritems()}
    w, h, tx, ty = position['width'], position['height'], position['left'], position['top']
    height, width = max(height, h + ty), max(width, w + tx)
  return height, width


def _svgRect(draw, attrs):
  """
  Helper function to draw a SVG rectangle.

  Args:
    draw: The svgwrite drawing context to create the rectangle in.
    attrs: A dictionary of attribute-value pairs. The attributes 'x', 'y', 'width'
      and 'height' are required for rectangles. Optional parameters for rectangles
      include 'r', which set the corner radius.

  Returns:
    A svgwrite object representing the drawn rectangle.
  """
  x, y, w, h = attrs.pop('x'), attrs.pop('y'), attrs.pop('width'), attrs.pop('height')
  svg        = draw.rect(insert=(x, y), size=(w, h))
  if 'r' in attrs:
    r                    = attrs.pop('r')
    svg['rx'], svg['ry'] = r, r
  return _svgProperties(svg, attrs)


def _svgCirc(draw, attrs):
  """
  Helper function to draw a SVG circle.

  Args:
    draw: The svgwrite drawing context to create the circle in.
    attrs: A dictionary of attribute-value pairs. The attributes 'cx', 'cy' and 'r'
      are required for circles.

  Returns:
    A svgwrite object representing the drawn circle.
  """
  cx, cy, r = attrs.pop('cx'), attrs.pop('cy'), attrs.pop('r')
  svg = draw.circle(center=(cx, cy), r=r)
  return _svgProperties(svg, attrs)


def _svgPath(draw, attrs):
  """
  Helper function to draw a SVG path.

  Args:
    draw: The svgwrite drawing context to create the path in.
    attrs: A dictionary of attribute-value pairs. The attribute 'path' is
      required for paths.

  Returns:
    A svgwrite object representing the drawn path.
  """
  svg = draw.path(d=attrs.pop('path'))
  svg.fill(color='none')
  return _svgProperties(svg, attrs)


def _svgText(draw, attrs):
  """
  Helper function to draw a SVG text.

  Args:
    draw: The svgwrite drawing context to create the text in.
    attrs: A dictionary of attribute-value pairs. The attributes 'x', 'y' and
      'text' are required for text.

  Returns:
    A svgwrite object representing the drawn text.
  """
  x, y, text = attrs.pop('x'), attrs.pop('y'), attrs.pop('text')

  if type(text) is list:
    lineHeight = attrs.pop('lineHeight')
    svg        = draw.text("", insert=(x, y))
    for line in text:
      svg.add(draw.tspan(line, x=[x], dy=[lineHeight]))
  else:
    svg = draw.text(text, insert=(x, y))
  svg.update({'font-family': 'helvetica'})
  if 'transform' in attrs:
    trans = attrs.pop('transform')
    if trans[0] == 'r':
      svg.rotate(int(trans[1:]), center=(x, y))
  return _svgProperties(svg, attrs)


def _svgProperties(svg, attrs):
  """
  A helper function to apply a dictionary of attributes to an SVGWrite object.

  Args:
    svg: An svgwrite object.
    attrs: A dictionary of attributes to be applied to the svg object.

  Returns:
    An svgwrite object with all the properties of attrs applied.
  """
  for key, val in attrs.iteritems():
    try:
      if   key == 'clip-rect' and val:
        svg.clip_rect( top    = val[0]
                     , left   = val[1]
                     , right  = val[2]
                     , bottom = val[3] )
        svg['clip'] = 'rect({x}px,{y}px,{w}px,{h}px)'.format( x = val[0]
                                                            , y = val[1]
                                                            , w = val[2]
                                                            , h = val[3] )
      elif key.find('stroke') != -1 and val:
        keys = key.split('-')
        if len(keys) == 1:
          svg.stroke(color=getHex(val))
        elif keys[1] == 'width':
          svg.stroke(width=val)
        elif keys[1] == 'opacity':
          svg.stroke(opacity=val)
      elif key == 'fill':
        svg.fill(color=getHex(val))
      elif key == 'opacity':
        svg.fill(opacity=val)
      else:
        svg[key] = val
    except:
      pass # Need to handle anything?
  return svg, attrs

