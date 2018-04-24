# -*- coding: utf-8 -*-

def create_auction_document(self):
    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json, {"data": []})

    response = self.app.post('/auctions/{}/documents'.format(
        self.auction_id), upload_files=[('file', u'укр.doc', 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual(u'укр.doc', response.json["data"]["title"])
    if self.docservice:
        self.assertIn('Signature=', response.json["data"]["url"])
        self.assertIn('KeyID=', response.json["data"]["url"])
        self.assertNotIn('Expires=', response.json["data"]["url"])
        key = response.json["data"]["url"].split('/')[-1].split('?')[0]
        auction = self.db.get(self.auction_id)
        self.assertIn(key, auction['documents'][-1]["url"])
        self.assertIn('Signature=', auction['documents'][-1]["url"])
        self.assertIn('KeyID=', auction['documents'][-1]["url"])
        self.assertNotIn('Expires=', auction['documents'][-1]["url"])
    else:
        key = response.json["data"]["url"].split('?')[-1].split('=')[-1]

    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual(u'укр.doc', response.json["data"][0]["title"])

    response = self.app.get('/auctions/{}/documents/{}?download=some_id'.format(
        self.auction_id, doc_id), status=404)
    self.assertEqual(response.status, '404 Not Found')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['status'], 'error')
    self.assertEqual(response.json['errors'], [
        {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
    ])

    if self.docservice:
        response = self.app.get('/auctions/{}/documents/{}?download={}'.format(
            self.auction_id, doc_id, key))
        self.assertEqual(response.status, '302 Moved Temporarily')
        self.assertIn('http://localhost/get/', response.location)
        self.assertIn('Signature=', response.location)
        self.assertIn('KeyID=', response.location)
        self.assertNotIn('Expires=', response.location)
    else:
        response = self.app.get('/auctions/{}/documents/{}?download=some_id'.format(
            self.auction_id, doc_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location': u'url', u'name': u'download'}
        ])

        response = self.app.get('/auctions/{}/documents/{}?download={}'.format(
            self.auction_id, doc_id, key))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/msword')
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, 'content')

    response = self.app.get('/auctions/{}/documents/{}'.format(
        self.auction_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(u'укр.doc', response.json["data"]["title"])

    response = self.app.post('/auctions/{}/documents?acc_token=acc_token'.format(
        self.auction_id), upload_files=[('file', u'укр.doc'.encode("ascii", "xmlcharrefreplace"), 'content')])
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(u'укр.doc', response.json["data"]["title"])
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertNotIn('acc_token', response.headers['Location'])

    self.set_status('active.auction')

    response = self.app.post('/auctions/{}/documents'.format(
        self.auction_id), upload_files=[('file', u'укр.doc', 'content')], status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't add document in current (active.auction) auction status")


def put_auction_offline_document(self):
    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'Порядок ознайомлення з майном / Порядок ознайомлення з активом у кімнаті даних',
            'documentType': 'x_dgfAssetFamiliarization',
            'accessDetails': u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс'
        }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    self.assertIn(doc_id, response.headers['Location'])
    self.assertEqual(u'Порядок ознайомлення з майном / Порядок ознайомлення з активом у кімнаті даних', response.json["data"]["title"])
    self.assertEqual(u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс', response.json["data"]["accessDetails"])
    self.assertEqual('offline/on-site-examination', response.json["data"]["format"])
    self.assertEqual('x_dgfAssetFamiliarization', response.json["data"]["documentType"])
    dateModified = response.json["data"]['dateModified']
    datePublished = response.json["data"]['datePublished']

    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'Новий порядок ознайомлення',
            'documentType': 'x_dgfAssetFamiliarization',
        }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [
        {u'description': [u'This field is required.'], u'location': u'body', u'name': u'accessDetails'}
    ])

    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'Новий порядок ознайомлення',
            'documentType': 'x_dgfAssetFamiliarization',
            'accessDetails': u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс',
            'hash': 'md5:' + '0' * 32,
        }}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'], [{'description': [u'This field is not required.'], u'location': u'body', u'name': u'hash'}])

    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'Порядок ознайомлення з майном #2',
            'documentType': 'x_dgfAssetFamiliarization',
            'accessDetails': u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс'
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(u'Порядок ознайомлення з майном #2', response.json["data"]["title"])
    self.assertEqual(u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс', response.json["data"]["accessDetails"])
    self.assertEqual('offline/on-site-examination', response.json["data"]["format"])
    self.assertEqual('x_dgfAssetFamiliarization', response.json["data"]["documentType"])

    auction = self.db.get(self.auction_id)
    self.assertEqual(u'Порядок ознайомлення з майном #2', auction['documents'][-1]["title"])
    self.assertEqual(u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс', auction['documents'][-1]["accessDetails"])
    self.assertEqual('offline/on-site-examination', auction['documents'][-1]["format"])
    self.assertEqual('x_dgfAssetFamiliarization', auction['documents'][-1]["documentType"])

    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"][-1]["id"])
    self.assertEqual(u'Порядок ознайомлення з майном #2', response.json["data"][-1]["title"])
    self.assertEqual(u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс', response.json["data"][-1]["accessDetails"])
    self.assertEqual('offline/on-site-examination', response.json["data"][-1]["format"])
    self.assertEqual('x_dgfAssetFamiliarization', response.json["data"][-1]["documentType"])

    response = self.app.get('/auctions/{}/documents/{}'.format(self.auction_id, doc_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(u'Порядок ознайомлення з майном #2', response.json["data"]["title"])
    dateModified2 = response.json["data"]['dateModified']
    self.assertTrue(dateModified < dateModified2)
    self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]['dateModified'])
    self.assertEqual(response.json["data"]['datePublished'], datePublished)

    response = self.app.get('/auctions/{}/documents?all=true'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(dateModified, response.json["data"][0]['dateModified'])
    self.assertEqual(dateModified2, response.json["data"][1]['dateModified'])

    response = self.app.post_json('/auctions/{}/documents'.format(self.auction_id),
        {'data': {
            'title': u'Порядок ознайомлення з майном #3',
            'documentType': 'x_dgfAssetFamiliarization',
            'accessDetails': u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс'
        }})
    self.assertEqual(response.status, '201 Created')
    self.assertEqual(response.content_type, 'application/json')
    doc_id = response.json["data"]['id']
    dateModified = response.json["data"]['dateModified']
    self.assertIn(doc_id, response.headers['Location'])

    response = self.app.get('/auctions/{}/documents'.format(self.auction_id))
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(dateModified2, response.json["data"][0]['dateModified'])
    self.assertEqual(dateModified, response.json["data"][1]['dateModified'])

    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'Порядок ознайомлення з майном #4',
            'documentType': 'x_dgfAssetFamiliarization',
            'accessDetails': u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс'
        }})
    self.assertEqual(response.status, '200 OK')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(u'Порядок ознайомлення з майном #4', response.json["data"]["title"])
    self.assertEqual('x_dgfAssetFamiliarization', response.json["data"]["documentType"])

    auction = self.db.get(self.auction_id)
    self.assertEqual(u'Порядок ознайомлення з майном #4', auction['documents'][-1]["title"])
    self.assertEqual('x_dgfAssetFamiliarization', response.json["data"]["documentType"])

    self.set_status('active.auction')

    response = self.app.put_json('/auctions/{}/documents/{}'.format(self.auction_id, doc_id),
        {'data': {
            'title': u'Порядок ознайомлення з майном #5',
            'documentType': 'x_dgfAssetFamiliarization',
            'accessDetails': u'Ознайомитись з рогом єдинорога можна: 30 лютого, коли сонце зійде на заході, печера Ілона Маска, плато Азімова, Марс'
        }}, status=403)
    self.assertEqual(response.status, '403 Forbidden')
    self.assertEqual(response.content_type, 'application/json')
    self.assertEqual(response.json['errors'][0]["description"], "Can't update document in current (active.auction) auction status")