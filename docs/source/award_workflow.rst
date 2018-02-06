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

1. The awards are created for 2 participants whose bids were the highest within the auction. Note that the participants with valid bids only can be qualified.  
2. The award with the highest valid bid initially receives `pending.verification` status (the second one is in `pending.waiting`). The procedure enters the verificationPeriod phase (status: `active.qualification`). When the protocol is uploaded and confirmed by the Organizer, the award should be manually switched to `pending.payment` status. Simultaneously the procedure enters the signingPeriod phase (status: `active.awarded`).
3. When the payment has been received, the Organizer should switch award to `active`. Thereby, the contract is being created for this award in `pending` status and the procedure enters the signingPeriod phase (status: `active.awarded`). Within this stage the Organizer should upload the document and switch contract to active.
4. For the next bidder to be qualified, the Organizer should check the status of the previous one to unsuccessful first and then switch the next award to pending.verification.

Notes
-----

1. For the bidder to be qualified and not invalidated, his/her bid should be equal to or exceed the starting price of the auction + the minimal step of the auction.
    * In case the first two highest bids do not exceed the amount of starting price + the minimal step, the awards are not being formed at all, and the procedure automatically becomes “unsuccessful”.
    * In case the second highest bid is smaller than the starting price + the minimal step, two awards are formed with the smaller one becoming unsuccessful immediately. The first highest bid (if larger than the starting price + minimum step) undergoes the awarding procedure and can win the auction.
2. The Organizer can disqualify the award at any stage of the awarding process up until the moment, when the contract has been uploaded and activated in the system.
3. The second highest qualifying bidder can disqualify himself/herself (switch award to `cancelled`) at any point of time BEFORE the start of his/her qualification process.
4. All of the statuses are switched manually. Start and end dates of the periods do not influence the actions available to be done (completed).
5. In case of the Organizer noted minNumberOfQualifiedBids: 1 and only one bidder submitted the proposal, the auction would be oveleaped and this participant would become the qualified one.

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
