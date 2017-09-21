.. Description of client/server SaaS operation.	

###############################
TotalDepth and SaaS
###############################

This design shows the potential for running TotalDepth as *Software as a Service* (SaaS) or, if you prefer, *Cloud Computing*.

The design envisages a server running the full TotalDepth software and any number of clients running sub-sets of that software. Client software could be in-browser or on-device.

Network speed (i.e. latency+bandwidth) is crucial to the performance of this system and the network connection between the client and the server could be any of these (in order of slowness):

* A client and a server both running on the client's machine.
* A client device and a server running on a high speed LAN.
* A client device communicating with a server via a VPN.
* A client device communicating with a remote server via the internet.

TotalDepth accommodates all of these.

****************************************************
Processing Server Side Files
****************************************************

There is no particular challenge here as the server has all it needs to process any client instruction. The big disadvantage is that the client has to upload the file to the server before they can do anything. For small jobs on large files that can impose an disproportionate cost.

****************************************************
Processing Files that Remain on the Client's Device
****************************************************

The real challenge is: the client has a (very large?) file and wants to do something small (or at least incremental) with it, for example "Plot curves XYZ from 5840 to 5600 feet using format ABC" and the server only needs a tiny fraction of that file. Regardless of the network connection there should be some cunning in extracting the data that the client needs in minimal time. TotalDepth's indexing technique makes this possible.

This design shows how the client can work with the server without the tedious business of the client having to upload the complete file to the server. Instead the client and server cooperate to make sure that the minimum data is transferred for the immediate task in hand. 

The design is illustrated below, the client is on the left:

.. image:: images/Slide12.png

Starting the session
======================================

The session is initialised by the user requesting the client to operate on a particular file on the clients device. The client passes basic file information to the server and receives a unique session ID.

The Session ID
-----------------

The session ID could be a portable file ID, such as a checksum. Thus two users using the same file could benefit from each others read transactions. This would require copy-on-write and session ID modification.

Another optimisation when using a checksum is that if the server already has an exact copy of the file (using the checksum as a proxy for that) then the server could provide data from its own copy of the file without the user having to transfer any data to the server at all.

Session Bootstrapping
----------------------

Given a valid session ID the client code reads the minimum structural information for the server to comprehend (and mirror) the file structure. This will vary according to the file format (and will vary according to file size).

LIS
^^^^^^^^^^^^^^^^^^^^^

The client code must be capable of processing TIF markers, Physical Record headers and trailers and Logical Record headers. The client passes this data as an ordered list of pairs ``[(tell, bytes), ...]`` where tell is the ``size_t`` position in the of the Physical Record (or TIF marker) that starts the Logical Record and ``bytes`` is the raw two bytes of the Logical Record Header.

LAS
^^^^^^^^^^^^^^^^^^^^^

As LAS files are small and do not lend themselves easily to efficient indexing then, most likely, it is worth passing the
entire client file to the server.

RP66
^^^^^^^^^^^^^^^^^^^^^
This will be similar to LIS bootstrapping with the client code processing Visible Record Headers and Logical Record segments.

Index Completion
-----------------------
The bootstrap information passed to the server allows the server to construct a virtual, partial, logical image of the file. The server may request further information in the form of an ordered list of pairs ``[(file position, number of bytes), ...]``. The client does a series of seek/read operations and passes the data back to the server as a list of pairs ``[(file position, bytes), ...]``. This allows the server to complete the file index.

The total size of the data transferred to the server at this stage is typically 0.6% of the file size. See :ref:`TotalDepth-tech-indexing` for a description of how LIS files are indexed and :ref:`TotalDepth-tech-indexing.IndexSize` for a study of index sizes.

Rest of Session
=====================

Once bootstrapped any user request is passed by the client to the server, for example: "Plot curves ABC from 5840 to 5600 feet".

The server then consults its virtual file image to see if it has the data to satisfy the request. If so then the result of the request is sent to the client.

If the server does not have sufficient data in its virtual file image then the server will send to the client an (ordered) list of pairs ``[(file position, number of bytes), ...]``. The client does a series of seek/read operations on each pair and and passes the data back to the server as a list of pairs ``[(file position, bytes), ...]``. The server adds these to its virtual file image. The server then can complete the request.

Over time the virtual file image would grow but only as fast as the user's (new) demands.

Data Persistence
===================

It is possible for the server to persist the virtual file image over any number of sessions, this would improve the performance even further.

****************************************************
SaaS Pros and Cons
****************************************************

Advantages
==================

* Low barrier to use: browser based, no installation.
* Cross Platform: desktop, tablet, mobile etc.
* Minimum client code.
* Continuous software version update from the server.
* Integrated with other Internet services for example mapping data.
* Tailored appearance per client.
* Cloud availability behind the server.
* All usage data is available on server logs.

Disadvantages
========================

* Requires network connection (could have a server version running locally).
* User agent variability.
* Speed/performance limited by network.
* Server infrastructure and investment.
* Continuous maintenance and support.
* Security.
