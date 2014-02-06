###
# Define constants that are used throughout the codebase here.
###
#### Helpers to define skeletons for layers and aesthetics
createBasicAes = () ->
  #### Helper to define a skeleton for an aesthetic
  #
  # The basic aesthetic defines the type of allowable metrics, whether binning
  # is required for the aesthetic, the statistics that are allowable for the
  # aesthetic, and the default statistic to put on an aesthetic.
  type: ['num', 'cat', 'date']
  bin: false
  stat:
    cat: ['None', 'Count', 'Unique']
    num: ['None', 'Sum', 'Average', 'Count', 'Unique']
    date: ['None', 'Count', 'Unique', 'Mean']
  defaultStat:
    cat: 'None'
    num: 'None'
    date: 'None'

createBasicLayer = (name) ->
  #### Helper to define a skeleton for a layer
  #
  # A basic layer defines which aesthetics are visible, what each aesthetic
  # allows, and any restrictions on the aesthetics. This is largely dependent
  # on the type of chart this layer defines.
  visibleAes: ['x', 'y', 'color']
  x:     createBasicAes()
  y:     createBasicAes()
  color: createBasicAes()
  size:
    type: ['num']
    bin: false
    stat:
      num: ['None', 'Sum', 'Average', 'Count', 'Unique']
    defaultStat:
      cat:  'None'
      num:  'None'
      date: 'None'

#### Association tables for names displayed in statistics to internal keywords
stats            = {}
stats.nameToStat =
  'Count':   'count'
  'Unique':  'unique'
  'Sum':     'sum'
  'Average': 'mean'
stats.statToName = _.invert(stats.nameToStat)

#### UI constants
ui =
  grid_width: 12
  grid_size: 25

#### Create the basic layer types and associated options
LAYERNAMES = ['scatter', 'area', 'line', 'bar', 'tile', 'spline' # Cartesian
             , 'pie', 'star', 'spider', 'splider']               # Polar
layers = {}
for n in LAYERNAMES
  layers[n] = createBasicLayer()

# variation to each layer
layers.scatter.visibleAes = ['x', 'y', 'color', 'size']
layers.line.visibleAes    = ['x', 'y', 'color', 'size']

layers.bar.x.stat.num = ['None']
layers.bar.x.bin      = true
layers.bar.y.stat.num         =  ['None', 'Sum', 'Average', 'Count', 'Unique']
layers.bar.y.defaultStat.num  = 'Sum'
layers.bar.y.defaultStat.cat  = 'Count'
layers.bar.y.defaultStat.date = 'Count'
layers.bar.color.bin = true

layers.tile.x.bin = true
layers.tile.y.bin = true

layers.pie.visibleAes     = ['y', 'color']
layers.spider.visibleAes  = ['x', 'y', 'color', 'size']
layers.splider.visibleAes = ['x', 'y', 'color', 'size']

# Association list for type names; first is rectangular and second is polar
layers.names = [
  ['bar'    , 'pie']
  ['scatter', null]
  ['line'   , 'spider']
  ['spline' , null]
  ['tile'   , null]
  ['area'   , null]
]


#### Skeletons for facets, numerals and tables
facets =
  type: ['num', 'cat', 'date']
  bin: true
  stat:
    cat: ['None']
    num: ['None']
    date: ['None']
  defaultStat:
    cat: 'None'
    num: 'None'
    date: 'None'

numeral =
  value:
    type: ['num', 'cat']
    bin: false
    stat:
      cat: ['Count', 'Unique']
      num: ['Sum', 'Average', 'Count', 'Unique']
      date: ['Count']
    defaultStat:
      cat: 'Unique'
      num: 'Sum'
      date: 'Count'

table =
  quickadd:
    type: ['num', 'cat', 'date']
    bin: true
    stat:
      cat: ['None']
      date: ['None']
      num: ['Sum', 'Average', 'Count', 'Unique']
    defaultStat:
      cat: 'None'
      num: 'Sum'
      date: 'None'
  value:
    type: ['num', 'cat', 'date']
    bin: false
    stat:
      cat: ['Count', 'Unique']
      date: ['Count', 'Unique']
      num: ['Sum', 'Average', 'Count', 'Unique']
    defaultStat:
      cat: 'Count'
      num: 'Sum'
      date: 'Count'
  row:
    type: ['num', 'cat', 'date']
    bin: true
    stat:
      cat: ['None']
      date: ['None']
      num: ['None']
    defaultStat:
      cat: 'None'
      num: 'None'
      date: 'None'
  column:
    type: ['num', 'cat', 'date']
    bin: true
    stat:
      cat: ['None']
      date: ['None']
      num: ['None']
    defaultStat:
      cat: 'None'
      num: 'None'
      date: 'None'

module.exports =
  layers:   layers
  facets:   facets
  stats:    stats
  numeral:  numeral
  table :   table
  ui:       ui
