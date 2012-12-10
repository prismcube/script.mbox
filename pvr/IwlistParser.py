import sys
import re


FILE_TEMP						=	'/tmp/ip_temp'


def Get_name( aCell ) :
	return Matching_line( aCell, 'ESSID:' )[1:-1]


def Get_quality( aCell ) :
	quality = Matching_line( aCell, 'Quality=' ).split( )[0].split( '/' )
	return str( int( round( float( quality[0] ) / float( quality[1] ) * 100 ) ) ).rjust(3) + ' %'


def Get_encryption( aCell ) :
	enc = ''
	if Matching_line( aCell, 'Encryption key:' ) == 'off' :
		enc = 'No'
	else :
		for line in aCell :
			matching = Match( line, 'IE:' )
			if matching != None :
				words = matching.split( '/' )
				for word in words :
					wpa = Match( word, 'WPA Version ' )
					if wpa != None :
						enc = 'WPA'
					wpa2 = Match( word, 'WPA2 Version ' )
					if wpa2 != None :
						enc = 'WPA2'
		if enc == '' :
			enc = 'WEP'
	return enc


columns = [ 'Name', 'Quality', 'Encryption' ]
rules = { 'Encryption' : Get_encryption, 'Quality' : Get_quality, 'Name' : Get_name }


def Sort_cells( aCells ) :
	sortby = 'Quality'
	reverse = True
	aCells.sort( None, lambda el:el[sortby], reverse )


def Matching_line( aLines, aKeyword ) :
	for line in aLines :
		matching = Match( line , aKeyword )
		if matching != None :
			return matching
	return None


def Match( aLine, aKeyword ) :
	aLine = aLine.lstrip( )
	length = len( aKeyword )
	if aLine[:length] == aKeyword :
		return aLine[ length : ]
	else :
		return None


def Parse_cell( aCell ) :
	parsed_cell = {}
	for key in rules :
		rule = rules[ key ]
		parsed_cell.update( { key : rule( aCell ) } )
	return parsed_cell


def Get_ApList( ) :
	cells = [[]]
	parsed_cells = []
	openFile = open( FILE_TEMP, 'r' )
	inputline = openFile.readlines( )
	for line in inputline :
		cell_line = Match( line, "Cell " )
		if cell_line != None :
			cells.append( [] )
			line = cell_line[-27:]
		cells[-1].append( line.rstrip( ) )

	cells = cells[1:]

	for cell in cells :
		parsed_cells.append( Parse_cell( cell ) )

	Sort_cells( parsed_cells )

	table=[]
	for cell in parsed_cells:
		cell_properties = []
		for column in columns :
			cell_properties.append( cell[column] )
		table.append( cell_properties )

	return table
