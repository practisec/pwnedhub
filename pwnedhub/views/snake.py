from flask import Blueprint, request, g, abort
from sqlalchemy import desc
from pwnedhub import db
from pwnedhub.decorators import login_required
from common.models import Score
from urllib.parse import urlencode
import math
import re

snake = Blueprint('snake', __name__)

@snake.route('/<path:filename>')
@login_required
def snake_files(filename):
    rec_regex = r'rec(\d+)\.txt'
    if filename == 'highscores.txt':
        scores = Score.query.filter(Score.recid != None).order_by(Score.recid).all()
        scoreboard = []
        for i in range(0, len(scores)):
            scoreboard.append(('name'+str(i), scores[i].player))
            scoreboard.append(('score'+str(i), scores[i].score))
            scoreboard.append(('recFile'+str(i), scores[i].recid))
        return urlencode(scoreboard)
    elif re.search(rec_regex, filename):
        recid = re.search(rec_regex, filename).group(1)
        score = Score.query.filter_by(recid=recid).first()
        if not score:
            abort(404)
        return score.recording
    abort(404)

@snake.route('/enterHighscore.php', methods=['POST'])
@login_required
def snake_enter_score():
    status = 'no response'
    # make sure scorehash is correct for the given score
    score = int(request.form['score'])
    scorehash = int(request.form['scorehash'])
    if math.sqrt(scorehash - 1337) == score:
        if request.form['SNAKE_BLOCK'] == '1':
            # create recording string
            recTurn = request.form['recTurn']
            recFrame = request.form['recFrame']
            recFood = request.form['recFood']
            recData = urlencode({ 'recTurn':recTurn, 'recFrame':recFrame, 'recFood':recFood })
            # add the new score
            playerName = g.user.username#request.form['playerName']#re.sub('[&=#<>]', '', request.form['playerName'])
            score = Score(player=playerName, score=score, recording=recData)
            db.session.add(score)
            db.session.commit()
            # reset the high scores. the game requests rec#.txt files 0-9 by
            # default, so the recid field must be updated for the high scores
            # clear out current high scores
            for score in Score.query.all():
                score.recid = None
                db.session.add(score)
            db.session.commit()
            # update the recid field to set the new high scores
            scores = Score.query.order_by(Score.score.desc()).limit(10).all()
            for i in range(0, len(scores)):
                scores[i].recid = i
                db.session.add(scores[i])
            db.session.commit()
            status = 'ok'
        else:
            status = 'snake block not present'
    else:
        status = 'invalid scorehash'
    return urlencode({'status':status})
