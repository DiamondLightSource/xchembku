class ThingTypes:
    SWISS2 = "xchembku_api::crystal_plate_objects::swiss2"
    SWISS3 = "xchembku_api::crystal_plate_objects::swiss3"
    MITEGEN = "xchembku_api::crystal_plate_objects::mitegen"


# Names that appear in the Formulatrix database, and how they map to our class types.
TREENODE_NAMES_TO_THING_TYPES = {
    "SWISSci_3Drop": ThingTypes.SWISS3,
    "SWISSci_3drop": ThingTypes.SWISS3,
    # When adding these plate types, need to add corresponding entries to factory in crystal_plate_objects.py.
    # TODO: Add 2drop and mitegen plate types.
    # "SWISSci_2drop": ThingTypes.SWISS2,
    # "Mitegen_insitu1": ThingTypes.MITEGEN,
    # "MiTInSitu": ThingTypes.MITEGEN,
}
