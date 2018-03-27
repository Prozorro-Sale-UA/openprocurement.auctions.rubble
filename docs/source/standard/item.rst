.. . Kicking page rebuild 2014-10-30 17:00:08
.. include:: defs.hrst

.. index:: Item, Parameter, Classification, CAV, Unit

.. _Item:

Item
====

Schema
------

:id:
    string, auto-generated

:description:
    string, multilingual, required

    |ocdsDescription|
    A description of the goods, services to be provided.
    
    Auction subject / asset description.

:classification:
    :ref:`Classification`

    |ocdsDescription|
    The primary classification for the item. See the `itemClassificationScheme` to 
    identify preferred classification lists.

    Possible variants of available primary classifiers are CPV and CAV-PS. 
    Additionally, there is a validation for the input of these classifiers due to which 
    the accuracy of at least a class has to be used.

:additionalClassifications:
    List of :ref:`Classification` objects
    
    Additional classifier is CPVS. The property can be leased, when entering value PA01-7
    in the classifier CPVS field.

    |ocdsDescription|
    An array of additional classifications for the item. See the
    `itemClassificationScheme` codelist for common options to use in OCDS. 

:unit:
    :ref:`Unit`

    |ocdsDescription| 
    Description of the unit which the good comes in e.g.  hours, kilograms. 
    Made up of a unit name, and the value of a single unit.

:quantity:
    integer

    |ocdsDescription|
    The number of units required
    
:contractPeriod:
     :ref:`Period`
     
     The period which is used to indicate the duration of a contract within which it is valid.
     Contract period represents the start and end date for the contract signed after the property or asset has been sold.
     It is also can be used to specify the timeframe of a contact for a lease.
     
:address:
    :ref:`Address`

    Address, where the item is located.
    Classification codes (CAV-PS) for which `item.address` object is optional are given below:

    :download:`CPV <../tutorial/cpv_codes_item_address_optional.json>`

    :download:`CAV_v2 <../tutorial/cav_v2_codes_item_address_optional.json>`


:location:
    dictionary

    Geographical coordinates of the location. Element consists of the following items:

    :latitude:
        string, required
    :longitude:
        string, required
    :elevation:
        string, optional, usually not used

    `location` usually takes precedence over `address` if both are present.

.. :relatedLot:
    string

    ID of related :ref:`lot`.


.. _Classification:

Classification
==============

Schema
------

:scheme:
    string

    |ocdsDescription|
    A classification should be drawn from an existing scheme or list of
    codes.  This field is used to indicate the scheme/codelist from which
    the classification is drawn.  For line item classifications, this value
    should represent a known Item Classification Scheme wherever possible.

:id:
    string

    |ocdsDescription|
    The classification code drawn from the selected scheme.

:description:
    string

    |ocdsDescription|
    A textual description or title for the code.

:uri:
    uri

    |ocdsDescription|
    A URI to identify the code. In the event individual URIs are not
    available for items in the identifier scheme this value should be left
    blank.

.. _Unit:

Unit
====

Schema
------

:code:
    string, required

    UN/CEFACT Recommendation 20 unit code.

:name:
    string

    |ocdsDescription|
    Name of the unit
