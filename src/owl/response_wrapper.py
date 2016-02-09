# -*- coding: utf-8 -*-


class IterableWrapper():
    """ Wrap iterator to catch the StopIteration exception and mark the current
    call as done (makes it possible to calculate the total time of a request).
    """

    def __init__(self, end_cb, env, start, iterable):
        """
        :param end_cb: Function to call when the body was processed. The
            function gets called with the requests WSGI environment, the start
            time stamp and the request URL (without any query string).
        :type end_cb: function ({}, int, str)
        :type env: dict
        :type start: int
        :param iterable: The response body that should be wrapped.
        :type iterable: iterable
        """
        self._end_cb = end_cb
        self._env = env
        self._start = start
        self._iter = iter(iterable)

    def __iter__(self):
        return self

    def __next__(self):
        """ For iterating over the wrapped iterable, adding stuff to be done at
        the end of the iteration.
        """
        if self._iter is None:
            raise StopIteration()
        try:
            return self._iter.__next__()
        except StopIteration:
            # Build the request URL and call the end call back function.
            if self._env is not None and self._end_cb is not None:
                url = "{} {}://{}{}".format(
                    self._env.get("REQUEST_METHOD", "--"),
                    self._env.get("wsgi.url_scheme", "--"),
                    self._env.get("SERVER_NAME", "--"),
                    self._env.get("PATH_INFO"))
                self._end_cb(self._env, self._start, url)
            # Prevent memory leaks, clean out stuff which isn't needed anymore.
            self._end_cb = None
            self._env = None
            self._iter = None
            raise  # continue with end of iteration