"""
Este módulo se encarga de iniciar el servidor API, cargar la base de datos y agregar los endpoints.
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User, Ingredient, Cocktail, Dish, Favorite, Pairing
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from werkzeug.security import generate_password_hash
import logging

logging.basicConfig(level=logging.DEBUG)

api = Blueprint('api', __name__)

# Permitir solicitudes CORS
CORS(api)

# Endpoints sobre usuarios
@api.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users])

@api.route("/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.serialize())

@api.route("/new-user", methods=["POST"])
def create_user():
    data = request.json
    if not data:
        return jsonify({"error": "No se proporcionaron datos de entrada."}), 400
    
    password = data.get("password")
    if not password:
        return jsonify({"error": "La contraseña es obligatoria"}), 400
    
    hashed_password = generate_password_hash(password)
    new_user = User(
        name=data.get("name"),
        username=data.get("username"),
        email=data.get("email"),
        password=hashed_password
    )
    
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()), 200

@api.route("/user/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.json
    if not data:
        return jsonify({"error": "No se proporcionaron datos de entrada."}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    # Actualizar los campos solo si están presentes en la solicitud
    user.name = data.get("name", user.name)
    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)
    
    # Si se proporciona una nueva contraseña, actualizarla
    new_password = data.get("password")
    if new_password is not None:  # Cambiado de if new_password: a if new_password is not None:
        user.password = generate_password_hash(new_password)
    
    try:
        db.session.commit()
        return jsonify({"msg": "Usuario actualizado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api.route("/user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "Usuario eliminado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Endpoints sobre ingredientes
@api.route("/ingredients", methods=["GET"])
def get_ingredients():
    ingredients = Ingredient.query.all()
    return jsonify([ingredient.serialize() for ingredient in ingredients])

@api.route("/ingredient/<int:Ingredient_id>", methods=["GET"])
def get_ingredient(Ingredient_id):
    ingredient = Ingredient.query.get_or_404(Ingredient_id)
    return jsonify(ingredient.serialize())

@api.route("/ingredient", methods=["POST"])
def create_ingredient():
    data = request.json
    if not data:
        return jsonify({"error": "No se proporcionaron datos de entrada."}), 400
    
    ingredient_name = data.get("name")
    if not ingredient_name:
        return jsonify({"error": "El nombre del ingrediente es obligatorio."}), 400
    
    new_ingredient = Ingredient(
        name=data.get("name"),
        type=data.get("type")
    )
    
    db.session.add(new_ingredient)
    db.session.commit()
    return jsonify(new_ingredient.serialize()), 201

@api.route("/ingredient/<int:Ingredient_id>", methods=["PUT"])
def update_ingredient(Ingredient_id):
    data = request.json
    if not data:
        return jsonify({"error": "No se proporcionaron datos de entrada."}), 400
    
    ingredient = Ingredient.query.get(Ingredient_id)
    if not ingredient:
        return jsonify({"error": "Ingrediente no encontrado"}), 404
    
    ingredient.name = data.get("name", ingredient.name)
    
    try:
        db.session.commit()
        return jsonify({"msg": "Ingrediente actualizado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@api.route("/ingredient/<int:Ingredient_id>", methods=["DELETE"])
def delete_ingredient(Ingredient_id):
    ingredient = Ingredient.query.get(Ingredient_id)
    if not ingredient:
        return jsonify({"error": "Ingrediente no encontrado"}), 404
    
    try:
        db.session.delete(ingredient)
        db.session.commit()
        return jsonify({"msg": "Ingrediente eliminado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



 # endpoints cocktails

@api.route("/cocktails", methods=["GET"])
def get_cocktails():
    # Obtiene todos los cócteles
    cocktails = Cocktail.query.all()
    return jsonify([cocktail.serialize() for cocktail in cocktails])


@api.route("/cocktail/<int:Cocktail_id>", methods=["GET"])
def get_cocktail(Cocktail_id):
    # Obtiene el cóctel por el id
    cocktail = Cocktail.query.get_or_404(Cocktail_id)
    return jsonify(cocktail.serialize())


@api.route("/cocktail", methods=["POST"])
def create_cocktail():
    # Busca la data
    data = request.json
    if not data:
        return jsonify({"Error": "No se proporcionaron datos de entrada."}), 400

    # Obtiene los campos necesarios
    cocktail_name = data.get("name")
    preparation_steps = data.get("preparation_steps")
    flavor_profile = data.get("flavor_profile")
    user_id = data.get("user_id")

    # Verificaciones de campos requeridos
    if not cocktail_name:
        return jsonify({"Error": "El nombre del cóctel es obligatorio."}), 400
    if preparation_steps is None:
        return jsonify({"Error": "Los pasos de preparación son obligatorios."}), 400
    if flavor_profile not in ['sweet', 'sour', 'bitter']:  
        return jsonify({"Error": "El perfil de sabor debe ser válido."}), 400
    if user_id is None:
        return jsonify({"Error": "El ID del usuario es obligatorio."}), 400

    # Nuevo cóctel
    new_cocktail = Cocktail(
        name=cocktail_name,
        preparation_steps=preparation_steps,
        flavor_profile=flavor_profile,
        user_id=user_id  
    )

    db.session.add(new_cocktail)
    db.session.commit()
    
    return jsonify(new_cocktail.serialize()), 201



@api.route("/cocktail/<int:Cocktail_id>", methods=["PUT"])
def update_cocktail(Cocktail_id):
    data = request.json
    if not data:
        return jsonify({"Error": "No se proporcionaron datos de entrada."}), 400
    # Busca el cóctel por el id
    cocktail = Cocktail.query.get(Cocktail_id)
    # Si no lo encuentra
    if not cocktail:
        return jsonify({"Error": "Cóctel no encontrado."}), 404
    # Actualización cóctel
    cocktail.name = data.get("name", cocktail.name)
    cocktail.preparation_steps = data.get("preparation_steps", cocktail.preparation_steps)
    cocktail.flavor_profile = data.get("flavor_profile", cocktail.flavor_profile)
    try:
        db.session.commit()
        return jsonify({"Success": "Cóctel actualizado correctamente."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"Error": str(e)}), 500


@api.route("/cocktail/<int:Cocktail_id>", methods=["DELETE"])
def delete_cocktail(Cocktail_id):
    # Busca el cóctel
    cocktail = Cocktail.query.get(Cocktail_id)
    if not cocktail:
        return jsonify({"Error": "Cóctel no encontrado."}), 404
    try:
        # Elimina
        db.session.delete(cocktail)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"Error": str(e)}), 500

    return jsonify({"msg": "Cóctel eliminado correctamente."})


# endpoints platos
@api.route("/dishes", methods=["GET"])
def get_dishes():
    # Obtiene todos los platos
    dishes = Dish.query.all()
    return jsonify([dish.serialize() for dish in dishes])


@api.route("/dish/<int:Dish_id>", methods=["GET"])
def get_dish(Dish_id):
    # Obtiene el plato por el id o da error
    dish = Dish.query.get_or_404(Dish_id)
    return jsonify(dish.serialize())


@api.route("/dish", methods=["POST"])
def post_dish():
    data = request.json
    if not data:
        return jsonify({"Error": "No se proporcionaron datos de entrada."}), 400
    dish = data.get
    if not dish:
        return jsonify({"Error": "El plato es necesario."}), 400
    # Nuevo plato
    new_dish = Dish(
        name=data.get("name"),
        preparation_steps=data.get("preparation_steps"),
        flavor_profile=data.get("flavor_profile")
    )
    db.session.add(new_dish)
    db.session.commit()
    return jsonify(new_dish.serialize())


@api.route("/dish/<int:Dish_id>", methods=["PUT"])
def update_dish(Dish_id):
    # Convierte la data json
    data = request.json
    if not data:
        return jsonify({"Error": "No se proporcionaron datos de entrada."}), 400
    # Busca el plato por el id
    dish = Dish.query.get(Dish_id)
    if not dish:
        return jsonify({"Error": "Plato no encontrado."}), 404
    # Actualización del plato
    dish.name = data.get("name", dish.name)
    dish.preparation_steps = data.get("preparation_steps", dish.preparation_steps)
    dish.flavor_profile = data.get("flavor_profile", dish.flavor_profile)
    try:
        db.session.commit()
        return jsonify({"Success": "Plato actualizado correctamente."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"Error": str(e)}), 500


@api.route("/dish/<int:Dish_id>", methods=["DELETE"])
def delete_dish(Dish_id):
    # Obtiene plato por id
    dish = Dish.query.get(Dish_id)
    if not dish:
        return jsonify({"Error": "Plato no encontrado."}), 404
    try:
        # Elimina
        db.session.delete(dish)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"Error": str(e)}), 500

    return jsonify({"msg": "Plato eliminado correctamente."})


# endpoints favoritos
@api.route("/favorites", methods=["GET"])
def get_favourites():
    # Obtiene todos los favoritos
    favorites = Favorite.query.all()
    return jsonify([favorite.serialize() for favorite in favorites])


@api.route("/get-favorite/<int:favorite_id>", methods=["GET"])
def get_favorite(favorite_id):
    # Obtiene el favorito por el id o da error
    favorite = Favorite.query.get_or_404(favorite_id)
    return jsonify(favorite.serialize())


@api.route("/favorite", methods=["POST"])
def create_favorite():
    # Convierte la data a json
    data = request.json
    if not data:
        return jsonify({"Error": "No se proporcionaron datos de entrada."}), 400
    # Necesario
    user_id = data.get('user_id')
    cocktail_id = data.get('cocktail_id')
    dish_id = data.get('dish_id')
    # Si no encuentra ningún id asociado a ningún plato o cóctel
    if not user_id or (not cocktail_id and not dish_id):
        return jsonify({"Error": "Se requieren el ID de usuario y ya sea el ID de cóctel o de plato."}), 400
    # Si encuentra un id de plato y de cóctel
    if cocktail_id and dish_id:
        return jsonify({"Error": "Solo puedes marcar como favorito un plato o un cóctel, no ambos."}), 400

    # Crear el favorito
    new_favorite = Favorite(
        user_id=user_id,
        cocktail_id=cocktail_id,
        dish_id=dish_id
    )

    try:
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify(new_favorite.serialize()), 201
    except Exception as e:
        db.session.rollback()
        # Agregar el logging del error
        logging.exception("Ocurrió un error durante la creación del favorito.")
        # Devolver el mensaje de error exacto
        return jsonify({"Error": str(e)}), 500


@api.route("/favorite/<int:fav_id>", methods=["PUT"])
def update_favorite(fav_id):
    data = request.json
    if not data:
        return jsonify({"Error": "No se proporcionaron datos de entrada."}), 400

    # Obtener los nuevos valores de cocktail_id y dish_id
    cocktail_id = data.get('cocktail_id')
    dish_id = data.get('dish_id')

    # Verificar si al menos uno de los IDs se proporciona
    if not cocktail_id and not dish_id:
        return jsonify({"Error": "Se requiere el ID de cóctel o el ID de plato."}), 400

    # Buscar el favorito existente
    favorite = Favorite.query.get(fav_id)
    if not favorite:
        return jsonify({"Error": "Favorito no encontrado."}), 404

    # Actualizar los campos según los datos proporcionados
    if cocktail_id is not None:
        favorite.cocktail_id = cocktail_id
    if dish_id is not None:
        favorite.dish_id = dish_id

    try:
        db.session.commit()
        return jsonify(favorite.serialize()), 200
    except Exception as e:
        db.session.rollback()
        # Registrar el error para depuración
        logging.error("Error al guardar en la base de datos: %s", str(e))
        return jsonify({"Error": str(e)}), 500


@api.route("/favorite/<int:favorite_id>", methods=["DELETE"])
def delete_favorite(favorite_id):
    favorite = Favorite.query.get(favorite_id)
    if not favorite:
        return jsonify({"Error": "Favorito no encontrado."}), 404

    try:
        # Elimina
        db.session.delete(favorite)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"Error": str(e)}), 500

    return jsonify({"msg": "Favorito eliminado"}), 200





@api.route("/pairings", methods=["GET"])
def get_pairings():
    pairings = Pairing.query.all()
    return jsonify([pairing.serialize() for pairing in pairings])


@api.route("/pairing/<int:pairing_id>", methods=["GET"])
def get_pairing(pairing_id):
    # obtiene el emparejamiento por el id o da error
    pairing = Pairing.query.get_or_404(pairing_id)
    return jsonify(pairing.serialize())


@api.route("/pairing", methods=["POST"])
def create_pairing():
    data = request.get_json()

    user_id = data.get('user_id')
    cocktail_id = data.get('cocktail_id')
    dish_id = data.get('dish_id')

    if not all([user_id, cocktail_id, dish_id]):
        return jsonify({'error': 'Faltan campos requeridos'}), 400

    new_pairing = Pairing(user_id=user_id, cocktail_id=cocktail_id, dish_id=dish_id)

    db.session.add(new_pairing)
    db.session.commit()

    return jsonify(new_pairing.serialize()), 201


@api.route('/pairing/<int:pairing_id>', methods=['PUT'])
def update_pairing(pairing_id):
    data = request.get_json()
    pairing = Pairing.query.get_or_404(pairing_id)

    # Actualizar los campos si están presentes en la solicitud
    if 'user_id' in data:
        pairing.user_id = data['user_id']
    if 'cocktail_id' in data:
        pairing.cocktail_id = data['cocktail_id']
    if 'dish_id' in data:
        pairing.dish_id = data['dish_id']

    db.session.commit()

    return jsonify(pairing.serialize()), 200


@api.route('/pairing/<int:pairing_id>', methods=['DELETE'])
def delete_pairing(pairing_id):
    pairing = Pairing.query.get_or_404(pairing_id)

    db.session.delete(pairing)
    db.session.commit()

    return jsonify({"mensaje": "Emparejamiento eliminado correctamente"}), 200





if __name__ == '__main__':
    api.run(debug=True)