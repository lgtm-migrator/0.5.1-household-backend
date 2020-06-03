from flask import Blueprint, jsonify, current_app, request
from app.models import House, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils import error_missing_json_key
import jwt
from app import db

house_blueprint = Blueprint("house", __name__, url_prefix="/house")


@house_blueprint.route("/add", methods=("POST",))
@jwt_required
def add_house():
    try:
        name = request.json["name"]
        description = request.json["description"]
    except TypeError:
        return error_missing_json_key("name", "description")
    user = get_jwt_identity()
    db_user: User = User.query.get(user)
    house = House(name=name, description=description)
    db_user.houses.append(house)
    db.session.add(house)
    db.session.commit()
    db.session.refresh(house)
    return jsonify(
        msg="Created that house succesfully.", data=house.id, status="success"
    )


@house_blueprint.route("/house/user/join")
@jwt_required
def join_house():
    user = get_jwt_claims()
    db_user: User = User.query.get(user["id"])
    if not user:
        return (
            jsonify(msg="The supplied token was invalid.", status="error", data=""),
            400,
        )
    token = request.args.get("token")
    if not token:
        return (
            jsonify(msg="The supplied token was invalid.", status="error", data=""),
            400,
        )
    try:
        decoded_token = jwt.decode(token, current_app.config["SECRET_KEY"])
        if decoded_token["token_type"] == "specific_join_house":
            if db_user.id == decoded_token["user_id"]:
                User.houses.append(House.query.get(decoded_token["house_id"]))
                db.session.commit()
                return jsonify(
                    {
                        "msg": "You are now in this house.",
                        "data": house.id,
                        "status": "success",
                    }
                )
            else:
                return jsonify(
                    {
                        "msg": "You cannot use this token – it is for someone else.",
                        "status": "error",
                        "data": "",
                    }
                )
    except jwt.DecodeError:
        return (
            jsonify(msg="The supplied token was invalid.", status="error", data=""),
            400,
        )


@house_blueprint.route("/house/<int:house_id>/user/invite/<string:identifier>")
def specific_email(house_id, identifier):
    house = House.query.get(house_id)
    if not house.users.filter(
        (User.username == identifier) | (User.email == identifier)
    ).first():
        return jsonify(
            {
                "status": "error",
                "msg": "You don't have permission to do this",
                "data": "",
            }
        )
    user = User.filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()
    if not user:
        return (
            jsonify(
                {"msg": "That user could not be found.", "status": "error", "data": ""}
            ),
            404,
        )
    if house:
        token = jwt.encode(
            {
                "token_type": "specific_join_house",
                "house_id": house.id,
                "user_id": user.id,
            },
            current_app.config["SECRET_KEY"],
        )
        return jsonify(
            {
                "msg": "Successfully created an invite link",
                "status": "success",
                "data": token,
            }
        )
    else:
        return (
            jsonify(
                status="error", msg="A house with that ID cannot be found", data=""
            ),
            404,
        )


@house_blueprint.route("/house/<int:house_id>/user/invite")
def generic_invite(house_id):
    house = House.query.get(house_id)
    if house:
        token = jwt.encode(
            {"token_type": "generic_join_house", house_id: house.id},
            current_app.config["SECRET_KEY"],
        )
        return jsonify(data=token, msg="", status="success")
    else:
        return (
            jsonify(
                status="error", msg="A house with that ID cannot be found.", data=""
            ),
            404,
        )
