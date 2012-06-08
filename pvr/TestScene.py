from LircTestSender import KeyCode
key = KeyCode()

def test1():

	testScene =[
		#main menu
		[ key.VKEY_MENU, 4],
		[ key.VKEY_BACK, 4],
		[ key.VKEY_MENU, 4],
		[ key.VKEY_DOWN, 4],
		[ key.VKEY_DOWN, 4],
		[ key.VKEY_DOWN, 4],
		[ key.VKEY_BACK, 4],

		#channel list
		[ key.VKEY_OK, 4],
		[ key.VKEY_DOWN, 4],
		[ key.VKEY_OK, 4],
		[ key.VKEY_DOWN, 4],
		[ key.VKEY_OK, 4],
		[ key.VKEY_DOWN, 4],
		[ key.VKEY_OK, 4],
		[ key.VKEY_BACK, 4],

		#Live Plate
		[ key.VKEY_INFO, 4],
		[ key.VKEY_OK, 4],
		[ key.VKEY_BACK, 4],
		[ key.VKEY_PROG_UP, 4],
		[ key.VKEY_PROG_UP, 4],
		[ key.VKEY_PROG_UP, 4],
		[ key.VKEY_PROG_UP, 4],
		[ key.VKEY_BACK, 4]
	]
	return testScene

def test2():
	testScene =[
		#main menu
		[ key.VKEY_OK, 10],
		[ key.VKEY_BACK, 5]
	]
	return testScene

def test3():
	testScene =[
		#live
		[ key.VKEY_INFO, 10],
		[ key.VKEY_BACK, 5]
	]
	return testScene

def test4():
	testScene =[
		#live
		[ key.VKEY_PROG_UP, 10]
	]
	return testScene


