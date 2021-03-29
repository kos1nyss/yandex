from flask import Flask, request
from flask_restful import Api, Resource
from data import db_session
from data.all_models import *
from data.__functions import *
import datetime

app = Flask(__name__)
api = Api(app)


class AddCouriers(Resource):
    def post(self):
        incorrect_couriers = []
        couriers = request.json['data']
        types = {tp.title: tp.id for tp in db_sess.query(Type).all()}
        ids = [c.courier_id for c in db_sess.query(Courier).all()]
        for courier in couriers:
            new_courier, correct = {}, True
            for key in courier:
                if key == 'courier_id':
                    if courier[key] in ids:
                        correct = False
                elif key == 'courier_type':
                    if courier[key] not in types:
                        correct = False
                        break
                    courier[key] = types[courier[key]]
                elif key == 'regions':
                    if not isinstance(courier[key], list):
                        correct = False
                        break

                    for region in courier[key]:
                        if not isinstance(region, int):
                            correct = False
                            break
                elif key == 'working_hours':
                    if not time_group_check(courier[key]):
                        correct = False
                        break
                else:
                    correct = False
                new_courier[key] = courier[key]

            if correct:
                req_keys = ['courier_type', 'regions', 'working_hours']
                for key in req_keys:
                    if key not in new_courier:
                        correct = False
                        break
            if correct:
                db_sess.add(Courier(**new_courier))
            else:
                incorrect_couriers.append(new_courier['courier_id'])
        if incorrect_couriers:
            return {'validation_error': {'couriers': [{'id': i} for i in incorrect_couriers]}}, 400
        db_sess.commit()
        return {'couriers': [{'id': courier['courier_id']} for courier in couriers]}, 201


class UpdateCouriers(Resource):
    def patch(self, courier_id):
        try:
            courier_id = int(courier_id)
        except ValueError:
            return {}, 400

        courier = db_sess.query(Courier).filter(Courier.courier_id == courier_id).first()
        if not courier:
            return {}, 400

        data = request.json
        for key in data:
            if key == 'courier_type':
                if not isinstance(data[key], str):
                    return {}, 400
                tp = db_sess.query(Type).filter(Type.title == data[key]).first()
                if tp:
                    courier.courier_type = tp.id
                else:
                    return {}, 400
            elif key == 'regions':
                if not isinstance(data[key], list):
                    return {}, 400

                for region in data[key]:
                    if not isinstance(region, int):
                        return {}, 400
                courier.regions = data[key]
            elif key == 'working_hours':
                for interval in data[key]:
                    if not isinstance(interval, str):
                        return {}, 400
                    if not time_check(interval):
                        return {}, 400
                courier.working_hours = data[key]
            else:
                return {}, 400

        orders = db_sess.query(Order).filter(Order.owner_id == courier.courier_id)
        for order in orders:
            if order.region not in courier.regions:
                order.status, order.owner_id, order.assign_id = 0, None, None
            elif not time_group_interact(order.delivery_hours, courier.working_hours):
                order.status, order.owner_id, order.assign_id = 0, None, None

        available_weight = db_sess.query(Type).filter(Type.id == courier.courier_type).first().weight
        orders = db_sess.query(Order).filter(Order.owner_id == courier.courier_id).all()
        orders.sort(key=lambda o: o.weight)
        for order in orders:
            if available_weight >= order.weight:
                available_weight -= order.weight
            else:
                order.status, order.owner_id, order.assign_id = 0, None, None
        if not orders:
            db_sess.query(Assign).filter(Assign.owner_id == courier.courier_id).delete()
        db_sess.commit()

        tp = db_sess.query(Type).filter(Type.id == courier.courier_type).first().title
        return {
            'courier_id': courier.courier_id,
            'courier_type': tp,
            'regions': courier.regions,
            'working_hours': courier.working_hours,
        }


class AddOrders(Resource):
    def post(self):
        incorrect_orders = []
        orders = request.json['data']
        ids = [o.order_id for o in db_sess.query(Order).all()]
        for order in orders:
            new_order, correct = {}, True
            for key in order:
                if key == 'order_id':
                    if order[key] in ids:
                        correct = False
                elif key == 'weight':
                    if not isinstance(order[key], float):
                        correct = False
                        break
                    if len(str(order[key]).split('.')[1]) > 2:
                        correct = False
                        break
                    if not (0.01 <= order[key] <= 50):
                        correct = False
                        break
                elif key == 'region':
                    if not isinstance(order[key], int):
                        correct = False
                        break
                elif key == 'delivery_hours':
                    if not time_group_check(order[key]):
                        correct = False
                        break
                else:
                    correct = False
                    break
                new_order[key] = order[key]
            if correct:
                req_keys = ['weight', 'region', 'delivery_hours']
                for key in req_keys:
                    if key not in new_order:
                        correct = False
                        break
            if correct:
                db_sess.add(Order(**new_order, status=0))
            else:
                incorrect_orders.append(order['order_id'])
        if incorrect_orders:
            return {'validation_error': {'orders': [{'id': i} for i in incorrect_orders]}}, 400
        db_sess.commit()
        return {'orders': [{'id': order['order_id']} for order in orders]}, 201


class AssignOrders(Resource):
    def post(self):
        try:
            c_id = request.json['courier_id']
        except KeyError:
            return {}, 400
        if not isinstance(c_id, int):
            return {}, 400
        courier = db_sess.query(Courier).filter(Courier.courier_id == c_id).first()
        if not courier:
            return {}, 400
        assign = db_sess.query(Assign).filter(Assign.owner_id == courier.courier_id,
                                              Assign.status.is_(False)).first()
        if not assign:
            courier_type = db_sess.query(Type).filter(Type.id == courier.courier_type).first()
            available_weight = courier_type.weight

            new_orders = db_sess.query(Order).filter(Order.status == 0,
                                                     Order.weight <= courier_type.weight,
                                                     Order.region.in_(courier.regions), ).all()
            correct_orders = []
            if not new_orders:
                return {'orders': []}
            for order in new_orders:
                if order.weight > available_weight:
                    continue
                if not time_group_interact(courier.working_hours, order.delivery_hours):
                    continue
                correct_orders.append(order)
                available_weight -= order.weight
                if available_weight == 0:
                    break

            if correct_orders:
                dt = datetime.datetime.now().isoformat()
                dt, ms = dt.split('.')
                ms = int(float('%.2f' % (int(ms) / 1000000)) * 100)

                new_assign = Assign(owner_id=courier.courier_id,
                                    type=courier.courier_type,
                                    datetime=f'{dt}.{ms}Z',
                                    status=False)
                db_sess.add(new_assign)

                for order in correct_orders:
                    order = db_sess.query(Order).filter(Order.order_id == order.order_id).first()
                    order.owner_id, order.status = courier.courier_id, 1
                    order.assign_id = new_assign.id

                db_sess.commit()

            response = {'orders': [{'id': order.order_id} for order in correct_orders]}
            if correct_orders:
                response['assign_time'] = new_assign.datetime
            return response
        orders = db_sess.query(Order).filter(Order.assign_id == assign.id).all()
        return {'orders': [{'id': order.order_id} for order in orders],
                'assign_time': assign.datetime}


class CompleteOrders(Resource):
    def post(self):
        data = request.json
        for key in ['courier_id', 'order_id', 'complete_time']:
            if key not in data:
                return {}, 400
        for key in data:
            if key == 'courier_id':
                if not isinstance(data[key], int):
                    return {}, 400
                courier = db_sess.query(Courier).filter(Courier.courier_id == data[key]).first()
                if not courier:
                    return {}, 400
            elif key == 'order_id':
                if not isinstance(data[key], int):
                    return {}, 400
                order = db_sess.query(Order).filter(Order.order_id == data[key],
                                                    Order.owner_id == data['courier_id'],
                                                    Order.status == 1).first()
                if not order:
                    return {}, 400
            elif key == 'complete_time':
                if not isinstance(data[key], str):
                    return {}, 400
                try:
                    time = datetime.datetime.fromisoformat(data[key][:-1] + '0000')
                except ValueError:
                    return {}, 400
            else:
                return {}, 400

        assign_time = db_sess.query(Assign).filter(Assign.id == order.assign_id).first()
        assign_time = datetime.datetime.fromisoformat(assign_time.datetime[:-1] + '0000')
        if time < assign_time:
            return {}, 400

        order.status = 2
        order.completed_by = courier.courier_type
        order.complete_time = data['complete_time']

        orders = db_sess.query(Order).filter(Order.owner_id == data['courier_id'],
                                             Order.status == 1,
                                             Order.order_id != order.order_id).all()
        if not orders:
            assign = db_sess.query(Assign).filter(order.assign_id == Assign.id).first()
            assign.status = True

        db_sess.commit()
        return {'order_id': data['order_id']}


class CourierInfo(Resource):
    def get(self, courier_id):
        try:
            courier_id = int(courier_id)
        except ValueError:
            return {}, 400

        courier = db_sess.query(Courier).filter(Courier.courier_id == courier_id).first()
        if not courier:
            return {}, 400
        response = {
            'courier_id': courier.courier_id,
            'courier_type': db_sess.query(Type).filter(
                Type.id == courier.courier_type).first().title,
            'working_hours': courier.working_hours,
            'regions': courier.regions,
            'earnings': 0
        }

        assigns = db_sess.query(Assign).filter(Assign.owner_id == courier.courier_id,
                                               Assign.status.is_(True)).all()
        types = {tp.id: tp.cf for tp in db_sess.query(Type).all()}
        for assign in assigns:
            response['earnings'] += 500 * types[assign.type]

        times_by_region = {}
        for assign in assigns:
            times = []
            orders = db_sess.query(Order).filter(assign.id == Order.assign_id).all()
            for order in orders:
                times.append((order.region, datetime.datetime.fromisoformat(
                    order.complete_time[:-1] + '0000').timestamp()))
            times.sort(key=lambda t: t[1])
            times = [(-1,
                      datetime.datetime.fromisoformat(
                          assign.datetime[:-1] + '0000').timestamp())] + times
            for i in range(1, len(times)):
                times_by_region[times[i][0]] = times_by_region.get(times[i][0], []) + \
                                               [times[i][1] - times[i - 1][1]]
        min_time_by_region = -1
        for region in times_by_region:
            average = sum(times_by_region[region]) / len(times_by_region[region])
            if min_time_by_region == -1 or average < min_time_by_region:
                min_time_by_region = average
        if min_time_by_region != -1:
            response['rating'] = float('{:,.2f}'.format(
                (60 * 60 - min(min_time_by_region, 60 * 60)) / (60 * 60) * 5))

        return response


if __name__ == '__main__':
    db_session.global_init()
    db_sess = db_session.create_session()

    types = db_sess.query(Type).all()
    if not types:
        foot = Type(id=1, title='foot', weight='10', cf=2)
        bike = Type(id=2, title='bike', weight='15', cf=5)
        car = Type(id=3, title='car', weight='50', cf=9)
        db_sess.add_all([foot, bike, car])
        db_sess.commit()

    api.add_resource(AddCouriers, '/couriers')
    api.add_resource(UpdateCouriers, '/couriers/<courier_id>')
    api.add_resource(AddOrders, '/orders')
    api.add_resource(AssignOrders, '/orders/assign')
    api.add_resource(CompleteOrders, '/orders/complete')
    api.add_resource(CourierInfo, '/couriers/<courier_id>')
    app.run(host='0.0.0.0', port=8080)
