from flask import url_for, Blueprint, send_file
from flask_login import login_required, current_user
from models import *
from database_utils import create_aembassador_photo
from exceptions import *
from utils import *
from io import BytesIO
from base import errorHandler

# add aevent API blueprint
aevent_api = Blueprint('aevent_api', __name__)

# default fields
aevent_photo_fields = [f for f in list_fields(aembassadorPhotos) if f != 'data']

# load app config file
config = load_config()
PHOTO_STORAGE_TYPE = config.get('photo_storage_type', 'database')

# json object to lookup Table objects by name
table_dict = {
    'aevents': aevent,
    'aembassadors': aembassador,
    'styles': Style,
    'categories': Category,
    'aembassador_photos': aembassadorPhotos
}

# API METHODS BELOW

@aevent_api.route('/aevents')
@aevent_api.route('/aevents/<id>')
@errorHandler
def get_aevents(id=None):
    args = collect_args()
    f = args.get('f', 'json')
    handler = toGeoJson if f.lower() == 'geojson' else lambda t: t
    fields = args.get('fields')

    if id:
        try:
            aevent = query_wrapper(aevent, id=int(id))[0]
            return jsonify(handler(to_json(aevent, fields)))
        except IndexError:
            raise InvalidResource

    # query as normal
    results = query_wrapper(aevent, **args)
    return jsonify(handler(to_json(results, fields)))

@aevent_api.route('/aevents/<id>/aembassadors')
@aevent_api.route('/aevents/<id>/aembassadors/<bid>')
def get_aembassadors_from_aevent(id=None, bid=None):
    if not id:
        raise InvalidResource

    # fetch aevent first
    aevent = query_wrapper(aevent, id=int(id))[0]
    args = collect_args()
    fields = args.get('fields')

    # fetch aembassadors
    if bid:
        try:
            aembassadors = aevent.aembassadors
            # should be a way to achieve this via filter or join?
            return jsonify(to_json([b for b in aembassadors if b.id ==int(bid)][0], fields))
        except:
            raise InvalidResource
    return jsonify(to_json(aevent.aembassadors, **collect_args()))

@aevent_api.route('/aembassadors')
@aevent_api.route('/aembassadors/<id>')
def get_aembassador_by_id(id=None):
    return endpoint_query(aembassador, id=id, **collect_args())

@aevent_api.route('/aembassadors/<id>/photos')
def get_aembassador_photos(id=None):
    if not id:
        raise InvalidResource

    aembassador = query_wrapper(aembassador, id=int(id))[0]
    return jsonify(to_json(aembassador.photos, aembassador_photo_fields))

@aevent_api.route('/aembassador/photos')
@aevent_api.route('/aembassador/photos/<id>')
def get_aembassador_photo(id=None):
    return endpoint_query(aembassadorPhotos, aembassador_photo_fields, id)

@aevent_api.route('/aembassador/categories')
@aevent_api.route('/aembassador/categories/<id>')
def get_categories(id=None):
    return endpoint_query(Category, id=id, **collect_args())

@aevent_api.route('/aembassador/categories/<id>/styles')
def get_category_styles(id):
    if id:
        try:
            category_styles = query_wrapper(Category, id=int(id))[0].styles
        except IndexError:
            raise InvalidResource
        return jsonify(to_json(category_styles, **collect_args()))
    raise InvalidResource

@aevent_api.route('/aembassador/styles')
@aevent_api.route('/aembassador/styles/<id>')
def get_styles(id=None):
    return endpoint_query(Style, id=id, **collect_args())


@aevent_api.route('/aembassador/photos/<id>/download')
def download_aembassador_photo(id):
    if not id:
        raise InvalidResource

    aembassador_photo = query_wrapper(aembassadorPhotos, id=int(id))[0]

    # handle appropriately based on config
    if PHOTO_STORAGE_TYPE == 'filesystem':
        to_send = os.path.join(upload_folder, aembassador_photo.photo_name)
    else:
        to_send = BytesIO(aembassador_photo.data)
    return send_file(to_send, attachment_filename=aembassador_photo.photo_name, as_attachment=True)


@aevent_api.route('/data/<tablename>/export', methods=['POST'])
@login_required
def export_table_data(tablename):
    if tablename == 'aembassador_photos':
        return dynamic_error(message='data export is not available for aembassador photos')
    table = table_dict.get(tablename)
    print(tablename, table)
    if table:
        args = collect_args()
        fields = args.get('fields')
        f = args.get('f')
        if f:
            del args['f']
        else:
            f = 'csv'
        if fields:
            del args['fields']

        outfile = export_data(table, fields, f, **args)
        return success('successfully exported data',
                       filename=os.path.basename(outfile),
                       url=url_for('static', filename=os.path.basename(outfile), _external=True))
    raise InvalidResource


# EDITING API BELOW

@aevent_api.route('/data/<tablename>/create', methods=['POST'])
@login_required
def create_item(tablename):

    table = table_dict.get(tablename)
    if table:
        args = collect_args()
        if current_user:
            args['created_by'] = current_user.id

        # check if related feature (aembassador, etc)
        obj = None
        if tablename == 'aembassadors' and 'aevent_id' in args:
            # must get aevent first
            aevent = get_object(table_dict['aevents'], id=args['aevent_id'])
            if not aevent:
                return dynamic_error(description='Missing aevent Information',
                                     message='A "aevent_id" is required in order to create a new aembassador')

            # now that we have a valid aevent, create the new aembassador and append to the aevent "aembassadors" attribute
            del args['aevent_id']
            obj = create_object(table, **args)
            aevent.aembassadors.append(obj)

        elif tablename == 'aembassador_photos' and 'aembassador_id' in args and 'photo' in args:
            # fetch aembassador parent first
            try:
                aembassador = query_wrapper(aembassador, id=args.get('aembassador_id'))[0]
            except:
                return dynamic_error(description='Missing aembassador ID', message='A aembassador ID is required for submitting a photo')
            photo_blob = args.get('photo')
            try:
                obj = table(**create_aembassador_photo(data=photo_blob.stream.read(), photo_name=photo_blob.filename))
            except Exception as e:
                return dynamic_error(message=str(e))
            aembassador.photos.append(obj)

        elif tablename == 'styles' and 'cat_id' in args:
            # fetch parent category first
            category = get_object(Category, id=args.get('cat_id'))
            return dynamic_error(description='Missing Category Information',
                                     message='A "cat_id" (category ID) is required in order to create a new aembassador style')
            del args['cat_id']
            obj = create_object(Style, **args)
            category.styles.append(obj)

        else:
            obj = create_object(table, **args)
            session.add(obj)

        if obj:
            # commit database transaction if we have a valid object
            session.commit()
            return success('Successfully created new item in "{}"'.format(tablename), id=obj.id)
        return dynamic_error(message='Missing parameters for creating a new {}'.format(tablename))

    raise InvalidResource


@aevent_api.route('/data/<tablename>/<id>/update', methods=['POST', 'PUT'])
@login_required
def update_item(tablename, id):
    table = table_dict.get(tablename)
    if table:
        obj = get_object(table, id=id)
        if not obj:
            raise InvalidResource
        args = collect_args()

        if tablename == 'aembassador_photos' and args.get('photo'):
            aembassador_photo = query_wrapper(table, id=id)[0]
            remove_filesystem_photo(aembassador_photo)

            photo_blob = args.get('photo')
            update_object(aembassador_photo, **create_aembassador_photo(data=photo_blob.stream.read(), photo_name=photo_blob.filename))
        else:
            update_object(obj, **args)
        session.commit()
        return success('Successfully updated item in "{}"'.format(tablename), id=obj.id)

    raise InvalidResource

@aevent_api.route('/data/<tablename>/<id>/delete', methods=['DELETE'])
@login_required
def delete_item(tablename, id):
    table = table_dict.get(tablename)
    if table:
        obj = get_object(table, id=id)
        if not obj:
            raise InvalidResource
        oid = obj.id

        # before deleting check if it is a aembassador or aembassador photo, if so
        # remove photo too if the storage type is filesystem
        photo_names = []
        if tablename == 'aembassadors':
            photo_names.extend([p.photo_name for p in obj.photos])
        elif tablename == 'aembassador_photos':
            photo_names.append(obj.photo_name)
        for photo_name in photo_names:
            try:
                os.remove(os.path.join(upload_folder, photo_name))
            except:
                pass

        # delete the actual record
        delete_object(obj)
        session.commit()
        return success('Successfully deleted item in "{}"'.format(tablename), id=oid)

    raise InvalidResource
