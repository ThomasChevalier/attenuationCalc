def confirmation(msg):
	answer = None
	while not valid(answer):
		answer = input(msg + " [Y/N] ")
	return positive(answer)


def valid(answer):
	return positive(answer) or negative(answer)


def positive(answer):
	return answer is not None and answer.lower() in ("y", "yes", "oui", "o")


def negative(answer):
	return answer is not None and answer.lower() in ("n", "no", "non")
