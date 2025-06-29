#! /usr/bin/env python3
# cars.py  23/06/2025  D.J.Whale

import ptag

#class CarsParser(ptag.PathClassifier):
#class CarsParser(ptag.VariableParser):
#class CarsParser(ptag.RuleParser):
class CarsParser(ptag.RecBuilder):
    HEADINGS = ("code", "state", "capacity", "occupancy", "occupancy_pc", "short_desc", "northing", "easting")
    QUOTED   = (True,   True,    False,      False,       False,          True,         False,       False)

    RULES = {
        "/Parking/Carpark":                         (ptag.RecBuilder.start_rec,),
        "/Parking/Carpark/SystemCodeNumber/":       (ptag.RecBuilder.store, "code"),
        "/Parking/Carpark/Capacity/":               (ptag.RecBuilder.store, "capacity"),
        "/Parking/Carpark/ShortDescription/":       (ptag.RecBuilder.store, "short_desc"),
        "/Parking/Carpark/Northing/":               (ptag.RecBuilder.store, "northing"),
        "/Parking/Carpark/Easting/":                (ptag.RecBuilder.store, "easting"),
        "/Parking/Carpark/State/":                  (ptag.RecBuilder.store, "state"),
        "/Parking/Carpark/Occupancy/":              (ptag.RecBuilder.store, "occupancy"),
        "/Parking/Carpark/OccupancyPercentage/":    (ptag.RecBuilder.store, "occupancy_pc"),
        #"/Parking/Carpark/FillRate/":               (store, "fill_rate"),
        #"/Parking/Carpark/ExitRate/":               (store, "exit_rate"),
        #"/Parking/Carpark/QueueTime/":              (store, "queue_time"),
        #"/Parking/Carpark/LastUpdated/":            (store, "last_updated"),
        "/Parking/Carpark~":                        (ptag.RecBuilder.end_rec,),
    }

    @staticmethod
    def do_parse_file(filename:str) -> None:
        """Parse a file, without the app needing to create a parser object"""
        CarsParser().parse_file(filename)

    @staticmethod
    def do_parse_from(iterable) -> None:
        """Parse any iterable, without the app needing to create a parser object"""
        CarsParser().parse_from(iterable)

if __name__ == "__main__":
    # wget -O cars.xml http://data.nottinghamtravelwise.org.uk/parking.xml
    FILENAME = "cars.xml"
    CarsParser.do_parse_file(FILENAME)

# END