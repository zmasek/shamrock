=======
History
=======

0.0.1 (27.04.2019.)
-------------------

* First release on PyPI.

0.0.2 (21.07.2020.)
-------------------

* Trefle.io changed so this release retains links to an old version that is to be removed.

0.1.0 (22.07.2020.)
-------------------

* Trefle.io updated so these things were changed:
    * Authorization is now handled through query parameter, copy module needed, new query_parameters property added and removed headers property.
    * Pagination handled through links in the body and made relative instead of absolute. No more page size.
    * Gzip response needed to unwrap the JSON response now. Will remove this in the future versions.
    * New bascic endpoints added for division classes, division orders and distributions.
    * Added new methods for client-side auth, selecting plants by distributions or genus, submitting errors and corrections.
    * Genuses endpoint renamed to genus.
    * Versioning of the API started so the url parameter in the constructor is split to base and relative urls.
    * Response changed to handle the added meta and links additions for the navigation.
* Added ShamrockException wrapper for the low level library exceptions.
