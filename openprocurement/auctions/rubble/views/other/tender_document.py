# -*- coding: utf-8 -*-
from openprocurement.auctions.core.utils import (
    json_view,
    context_unpack,
    APIResource,
    save_auction,
    apply_patch,
    opresource,
    get_now,
)
from openprocurement.auctions.core.validation import (
    validate_file_update,
    validate_file_upload,
    validate_patch_document_data,
)

from openprocurement.auctions.rubble.utils import (
    upload_file, get_file, invalidate_bids_data, generate_rectificationPeriod
)


@opresource(name='rubbleOther:Auction Documents',
            collection_path='/auctions/{auction_id}/documents',
            path='/auctions/{auction_id}/documents/{document_id}',
            auctionsprocurementMethodType="rubbleOther",
            description="Auction related binary files (PDFs, etc.)")
class AuctionDocumentResource(APIResource):

    def validate_document_editing_period(self, operation):
        auction_not_in_editable_state = (self.request.authenticated_role != 'auction' and self.request.validated['auction_status'] != 'active.tendering' or \
           self.request.authenticated_role == 'auction' and self.request.validated['auction_status'] not in ['active.auction', 'active.qualification'])

        auction = self.request.validated['auction']
        if auction_not_in_editable_state:
            self.request.errors.add('body', 'data', 'Can\'t {} document in current ({}) auction status'.format('add' if operation == 'add' else 'update', self.request.validated['auction_status']))
            self.request.errors.status = 403
            return
        if auction.rectificationPeriod.endDate < get_now() and self.request.authenticated_role != 'auction':
            self.request.errors.add('body', 'data', 'Document can be {} only during the rectificationPeriod period.'.format('added' if operation == 'add' else 'updated'))
            self.request.errors.status = 403
            return
        return True

    @json_view(permission='view_auction')
    def collection_get(self):
        """Auction Documents List"""
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(dict([
                (i.id, i.serialize("view"))
                for i in self.context.documents
            ]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}

    @json_view(permission='upload_auction_documents', validators=(validate_file_upload,))
    def collection_post(self):
        """Auction Document Upload"""
        if not self.validate_document_editing_period('add'):
            return
        document = upload_file(self.request)
        if self.request.authenticated_role != "auction":
            if not self.request.auction.rectificationPeriod:
                self.request.auction.rectificationPeriod = generate_rectificationPeriod(self.request.auction)
            invalidate_bids_data(self.request.auction)
        self.context.documents.append(document)
        if save_auction(self.request):
            self.LOGGER.info('Created auction document {}'.format(document.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_document_create'}, {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    @json_view(permission='view_auction')
    def get(self):
        """Auction Document Read"""
        document = self.request.validated['document']
        offline = bool(document.get('documentType') == 'x_dgfAssetFamiliarization')
        if self.request.params.get('download') and not offline:
            return get_file(self.request)
        document_data = document.serialize("view")
        document_data['previousVersions'] = [
            i.serialize("view")
            for i in self.request.validated['documents']
            if i.url != document.url or
            (offline and i.dateModified != document.dateModified)
        ]
        return {'data': document_data}

    @json_view(permission='upload_auction_documents', validators=(validate_file_update,))
    def put(self):
        """Auction Document Update"""
        if not self.validate_document_editing_period('update'):
            return
        document = upload_file(self.request)
        if self.request.authenticated_role != "auction":
            if not self.request.auction.rectificationPeriod:
                self.request.auction.rectificationPeriod = generate_rectificationPeriod(self.request.auction)
            invalidate_bids_data(self.request.auction)
        self.request.validated['auction'].documents.append(document)
        if save_auction(self.request):
            self.LOGGER.info('Updated auction document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json", permission='upload_auction_documents', validators=(validate_patch_document_data,))
    def patch(self):
        """Auction Document Update"""
        if not self.validate_document_editing_period('update'):
            return
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if self.request.authenticated_role != "auction":
            if not self.request.auction.rectificationPeriod:
                self.request.auction.rectificationPeriod = generate_rectificationPeriod(self.request.auction)
            invalidate_bids_data(self.request.auction)
        if save_auction(self.request):
            self.LOGGER.info('Updated auction document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'auction_document_patch'}))
            return {'data': self.request.context.serialize("view")}
