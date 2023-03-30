import random

from flask import Flask, jsonify, request

app = Flask(__name__)
app.config['groups'] = []
groups = []
@app.route('/group', methods=['POST'])
def create_group():
    data = request.json
    if 'name' not in data:
        return jsonify({'message': 'Name is required'}), 400
    group = {
        'id': len(app.config['groups']) + 1,
        'name': data['name'],
        'description': data.get('description', ''),
        'participants': []
    }
    participants = data.get('participants', [])
    for i, participant in enumerate(participants):
        if 'name' not in participant:
            return jsonify({'message': 'Name is required'}), 400
        group['participants'].append({
            'id': i + 1,
            'name': participant['name'],
            'wish': participant.get('wish', ''),
            'recipient': None
        })
    app.config['groups'].append(group)
    return jsonify({'id': group['id']}), 201

@app.route('/groups', methods=['GET'])
def get_groups():
    simplified_groups = []
    for group in app.config['groups']:
        simplified_group = {
            'id': group['id'],
            'name': group['name'],
            'description': group['description'],
        }
        simplified_groups.append(simplified_group)
    return jsonify(simplified_groups)


@app.route('/group/<int:group_id>', methods=['GET'])
def get_group(group_id):
    for group in app.config['groups']:
        if group['id'] == group_id:
            simplified_group = {
                'id': group['id'],
                'name': group['name'],
                'description': group['description'],
                'participants': []
            }
            for participant in group['participants']:
                simplified_participant = {
                    'id': participant['id'],
                    'name': participant['name'],
                    'wish': participant.get('wish', ''),
                    'recipient': participant.get('recipient', None)
                }
                simplified_group['participants'].append(simplified_participant)
            return jsonify(simplified_group)
    return jsonify({'message': 'Group not found'}), 404

@app.route('/group/<int:group_id>', methods=['PUT'])
def update_group(group_id):
    for group in app.config['groups']:
        if group['id'] == group_id:
            data = request.json
            group['name'] = data.get('name', group['name'])
            group['description'] = data.get('description', group['description'])
            return jsonify({'message': 'Group updated successfully'}), 200
    return jsonify({'message': 'Group not found'}), 404

@app.route('/group/<int:group_id>', methods=['DELETE'])
def delete_group(group_id):
    for i, group in enumerate(app.config['groups']):
        if group['id'] == group_id:
            del app.config['groups'][i]
            return jsonify({'message': 'Group deleted successfully'}), 200
    return jsonify({'message': 'Group not found'}), 404

@app.route('/participants/<int:participant_id>', methods=['GET'])
def get_participant(participant_id):
    for group in groups:
        for participant in group['participants']:
            if participant['id'] == participant_id:
                return jsonify(participant)
    return jsonify({'message': 'Participant not found'}), 404

@app.route('/group/<int:group_id>/participant', methods=['POST'])
def create_participant(group_id):
    for group in groups:
        if group['id'] == group_id:
            data = request.json
            participant = {
                'id': len(group['participants']) + 1,
                'name': data['name'],
                'wish': data.get('wish', ''),
                'recipient': None
            }
            group['participants'].append(participant)
            return jsonify({'id': participant['id']}), 201
    return jsonify({'message': 'Group not found'}), 404

@app.route('/group/<int:group_id>/participant/<int:participant_id>', methods=['DELETE'])
def delete_participant(group_id, participant_id):
    for group in groups:
        if group['id'] == group_id:
            for i in range(len(group['participants'])):
                if group['participants'][i]['id'] == participant_id:
                    del group['participants'][i]
                    return jsonify({'message': 'Participant deleted successfully'}), 200
            return jsonify({'message': 'Participant not found'}), 404
    return jsonify({'message': 'Group not found'}), 404

@app.route('/group/<int:group_id>/toss', methods=['POST'])
def perform_toss(group_id):
    for group in groups:
        if group['id'] == group_id:
            participants = group['participants']
            num_participants = len(participants)
            if num_participants < 3:
                return jsonify({'message': 'Cannot perform toss with less than 3 participants'}), 409
            recipients = participants.copy()
            for participant in participants:
                possible_recipients = [r for r in recipients if r['id'] != participant['id'] and r['recipient'] is None]
                if not possible_recipients:
                    return jsonify({'message': 'Cannot perform toss with the current participants and recipients. Please edit and try again.'}), 409
                recipient = random.choice(possible_recipients)
                recipient['recipient'] = participant
                recipients.remove(recipient)
            simplified_participants = []
            for participant in participants:
                simplified_participant = {
                    'id': participant['id'],
                    'name': participant['name'],
                    'wish': participant['wish'],
                    'recipient': {
                        'id': participant['recipient']['id'],
                        'name': participant['recipient']['name'],
                        'wish': participant['recipient']['wish']
                    }
                }
                simplified_participants.append(simplified_participant)
            return jsonify(simplified_participants)
    return jsonify({'message': 'Group not found'}), 404


@app.route('/group/<int:group_id>/participant/<int:participant_id>/recipient', methods=['GET'])
def get_recipient(group_id, participant_id):
    for group in groups:
        if group['id'] == group_id:
            for participant in group['participants']:
                if participant['id'] == participant_id:
                    recipient = participant['recipient']
                    if recipient is None:
                        return jsonify({'message': 'Participant has not yet been assigned a recipient'}), 404
                    return jsonify({k:v for k,v in recipient.items() if k != 'recipient'})
            return jsonify({'message': 'Participant not found'}), 404
    return jsonify({'message': 'Group not found'}), 404



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)