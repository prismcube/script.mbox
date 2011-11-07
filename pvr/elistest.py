

from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt


class ElisTest(object):
	def __init__(self):
		pass

	def testAll( self ):
		self.testPropEnum()
		self.testPropInt()

	def testPropEnum( self ):
		prop = ElisPropertyEnum( 'Last ServiceType' )
		print 'prop test %s' %prop.getProp()
		print 'prop test (TV): %s' %prop.getPropStringByIndex( 0 )
		print 'prop test (Radio): %s' %prop.getPropStringByIndex( 1 )		
		print 'prop test (Last ServiceType): %s' %prop.getName()
		print 'prop test (TV or Radio): %s' %prop.getPropString()
		prop.setProp( 2 )
		print 'prop test 2 Radio : %d %s' %( prop.getProp(), prop.getPropString())
		prop.setPropIndex( 0 )
		print 'prop test 1 TV : %d %s' %( prop.getProp(), prop.getPropString())
		prop.setPropString( 'Radio' )
		print 'prop test 2 Radio : %d %s' %( prop.getProp(), prop.getPropString())


	def testPropInt( self ):
		propInt = ElisPropertyInt( 'Audio Volume' )
		print 'propint test =%d' %propInt.getProp()
		propInt.setProp( 30 )
		print 'propint test =%d' %propInt.getProp()	
	
