.. _award_workflow: 

Award Workflow
==============

For a more detailed information see :ref:`award`

    * :ref:`Qualification`
    * :ref:`Confirming_qualification`
    * :ref:`Candidate_disqualification`
    * :ref:`Waiting_refusal`



.. graphviz::

    digraph G {
        subgraph cluster_1 {
            node [style=filled, color=lightblue];
            edge[style=dotted];
            "pending.waiting" -> cancelled;

            node [style=filled, color=lightgrey];
            edge[style=dashed];
            "pending.verification" -> unsuccessful;
            edge[style=dashed];
            "pending.payment" -> active;
            edge[style=dashed];
            "pending.waiting" -> "pending.verification";
            label = "Awarding Process";
            color=blue
        }
            edge[style=dashed];
            "pending.verification" -> "pending.payment";
            edge[style=dashed];
            active -> unsuccessful;
            
    }



Roles
-----

:Organizer:  dashed

:Participant: dotted


Procedure Description
---------------------

1. The award with the highest qualifying bid initially receives a "pending.verification" status. The procedure enters the "verificationPeriod" stage. When the protocol is uploaded and confirmed by the organizer, the award should be manually switched to "pending.payment" status.
2. When the organizer confirms that the payment has been received, the award has to be switched to the "active" status, while the procedure moves to the status "signingPeriod". Within this stage the organizer should upload and activate the contract in the system.
3. For the next bidder to be qualified, the organizer should check tha status of the previous one to "unsuccessful" first and then switch the next award to "pending.verification".

Notes
-----

1. The organizer can disqualify the award at any stage of the awarding process up until the moment, when the contract has been uploaded and activated in the system.
2. The second highest qualifying bidder can disqualify himself/herself at any point in time BEFORE the start of his/her qualification process.
3. The awards are formed for all of the bidders.
4. All of the statuses are switched manually. Start and end dates of the periods do not influence the actions available to be done (completed).  


Statuses
--------

:pending.waiting:
    The second highest valid bidder awaits for the qualification of the first highest valid bidder. The former can choose to refuse to wait and withdraw his security deposit.

:cancelled:
    Terminal status. The second highest valid bidder chose to withdraw his security deposit and not to wait for the highest valid bidder to be disqualified.

:pending.verification:
    Awaiting protocol upload and confirmation by the liquidator. The highest valid bidder is able to submit the protocol as well, although it is not sufficient to move to the next status. 

:pending.payment:
    Awaiting payment. Organizer can change the status to active by confirming the payment has been received. 

:active:
    Awaiting for the contract to be signed (uploaded and activated in the system by the organizer). 

:unsuccessful:
    Terminal status. The auction was unsuccessful. Can be switched to from any of the previous statuses by the organizer.
