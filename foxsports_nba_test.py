import unittest
from foxsports_nba_database import *
from foxsports_nba_plot import *

class TestDatabase(unittest.TestCase):

    # Test if Database is Imported Correctly
    def test_reset_database(self):
        reset_database()
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement = """SELECT * FROM Injuries"""
        cur.execute(statement)
        result_ls = cur.fetchall()
        self.assertEqual(len(result_ls[0]), 5)
        statement = """SELECT * FROM Teams"""
        cur.execute(statement)
        result_ls = cur.fetchall()
        self.assertEqual(len(result_ls[0]), 2)
        statement = """SELECT * FROM Players"""
        cur.execute(statement)
        result_ls = cur.fetchall()
        self.assertEqual(len(result_ls[0]), 3)
        statement = """SELECT Name FROM Injuries WHERE PlayerId = 2"""
        cur.execute(statement)
        result_ls = cur.fetchall()
        self.assertTrue(("Ankle", ) in result_ls)
        
class TestPlot(unittest.TestCase):

    # Test if Accumulator Function Works Correctly
    def test_dict_accum_helper(self):
        temp_dict = {}
        dict_accum_helper(temp_dict, "key", "value")
        self.assertEqual(temp_dict["key"], ["value"])
        self.assertEqual(len(temp_dict), 1)
        dict_accum_helper(temp_dict, "key", {"k":"v"})
        self.assertEqual(len(temp_dict), 1)
        self.assertEqual(len(temp_dict["key"]), 2)
        self.assertEqual(temp_dict["key"][1]["k"], "v")
    
    # Test if Player Data is Fetched Correctly
    def test_get_player_data(self):
        kyrie = get_player_data("kyrie")
        self.assertIsInstance(kyrie, dict)
        self.assertEqual(kyrie["name"], "Kyrie Irving")
        self.assertTrue(kyrie["team"] is not None)
        self.assertTrue(kyrie["injuries"] is not None)
        self.assertEqual(kyrie["injuries"][-1]['date'], '12/20/2013')
        self.assertEqual(kyrie["injuries"][-1]['injury'], 'Flu')
        paul_george = get_player_data("paul george")
        self.assertIsInstance(paul_george, dict)
        self.assertTrue(paul_george["team"] is not None)
        self.assertTrue(paul_george["injuries"] is not None)
        self.assertEqual(paul_george["injuries"][-1]['date'], '08/01/2014')
        self.assertEqual(paul_george["injuries"][-1]['injury'], 'Fractured Leg')

    # Test if Player Class is working correctly
    def test_player_class(self):
        chris = get_player_data("chris paul")
        chris_obj = Player(chris)
        self.assertEqual(chris_obj.name, "Chris Paul")
        self.assertTrue(chris_obj.team != "")
        self.assertTrue(chris_obj.injuries != {})
        self.assertIsInstance(chris_obj.injuries, list)

unittest.main()
