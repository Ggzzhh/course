let randomInt = function (nMin, nMax) {
    return Math.floor(Math.random() * (nMax - nMin) + nMin + 0.5);
};

let randomOpt = function () {
    // var arr = ['+', '-', '*', '/'];
    // return arr[randomInt(0, 3)];
    return '+';
};

function generateQuestion() {
    return '' + randomInt(1, 10) + ' ' + randomOpt() + ' ' +randomInt(1, 10)
}

function getAnswer(question){
    let answer;
    try {
        answer = eval(question)
    }
    catch (e) {
        console.log(e)
    }
    return answer === null ? 'error': answer;
}