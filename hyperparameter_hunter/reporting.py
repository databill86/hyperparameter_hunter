##################################################
# Import Own Assets
##################################################
from hyperparameter_hunter import exception_handler
from hyperparameter_hunter.settings import G
from hyperparameter_hunter.utils.general_utils import now_time, to_even, type_val

##################################################
# Import Miscellaneous Assets
##################################################
from contextlib import suppress
from datetime import datetime
import inspect
import logging
import os.path
import re
import warnings


class ReportingHandler(object):
    def __init__(self, heartbeat_path=None, float_format='{:.5f}', console_params=None, heartbeat_params=None, add_frame=False):
        """The class in control of custom logging methods, how logs are formatted, and initializing logging for Experiments

        Parameters
        ----------
        heartbeat_path: Str path, or None, default=None
            If string and valid heartbeat path, logging messages will also be saved in this file
        float_format: String, default='{:.5f}'
            If not default, must be a valid formatting string for floating point values. If invalid, default will be used
        console_params: Dict, or None, default=None
            Parameters passed to :meth:`configure_console_logger_handler`
        heartbeat_params: Dict, or None, default=None
            Parameters passed to :meth:`configure_heartbeat_logger_handler`
        add_frame: Boolean, default=False
            If True, whenever :meth:`log` is called, the source of the call will be prepended to the content being logged"""
        self.reporting_type = 'logging'  # TODO: Add `reporting_type` as kwarg to `__init__`, with options: logging, advanced
        self.heartbeat_path = heartbeat_path
        self.float_format = float_format
        self.console_params = console_params or {}
        self.heartbeat_params = heartbeat_params or {}
        self.add_frame = add_frame

        self.validate_parameters()

        #################### Configure Reporting ####################
        self.configure_reporting_type()

    def validate_parameters(self):
        #################### reporting_type ####################
        valid_types = ['logging', 'standard', 'advanced']
        if not isinstance(self.reporting_type, str):
            raise TypeError('reporting_type must be a str. Received {}: {}'.format(*type_val(self.reporting_type)))
        if self.reporting_type not in valid_types:
            raise ValueError('reporting_type must be in {}. Received: {}'.format(valid_types, self.reporting_type))

        #################### heartbeat_path ####################
        if self.heartbeat_path is not None:
            if not isinstance(self.heartbeat_path, str):
                raise TypeError('heartbeat_path must be of type str. Received {}: {}'.format(*type_val(self.heartbeat_path)))

            head, tail = os.path.split(self.heartbeat_path)

            if not tail.endswith('.log'):
                raise ValueError('heartbeat_path must end with the extension ".log". Received: {}'.format(self.heartbeat_path))
            if not os.path.exists(head):
                raise FileNotFoundError('heartbeat_path must start with an existing dir. Received {}'.format(self.heartbeat_path))

        #################### float_format ####################
        if not isinstance(self.float_format, str):
            raise TypeError('float_format must be a format str. Received {}: {}'.format(*type_val(self.float_format)))
        if (not self.float_format.startswith('{')) or (not self.float_format.endswith('}')):
            raise ValueError('float_format must start with "{{" and end with "}}". Received: {}'.format(self.float_format))

        #################### console_params ####################
        if not isinstance(self.console_params, dict):
            raise TypeError('console_params must be a dict or None. Received {}'.format(type(self.console_params)))

        #################### heartbeat_params ####################
        if not isinstance(self.heartbeat_params, dict):
            raise TypeError('heartbeat_params must be a dict or None. Received {}'.format(type(self.heartbeat_params)))

    def configure_reporting_type(self):
        if self.reporting_type == 'standard':
            raise ValueError('Standard logging is not yet implemented. Please choose "logging"')
            # setattr(self, 'log', self._standard_log)
            # setattr(self, 'debug', self._standard_debug)
            # setattr(self, 'warn', self._standard_warn)
        elif self.reporting_type == 'logging':
            setattr(self, 'log', self._logging_log)
            setattr(self, 'debug', self._logging_debug)
            setattr(self, 'warn', self._logging_warn)

            self.initialize_logging_logging()
        elif self.reporting_type == 'advanced':
            raise ValueError('Advanced logging is not yet implemented. Please choose one of: ["logging", "standard"]')

    def initialize_logging_logging(self):
        exception_handler.hook_exception_handler()

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        logger_handlers = [self.configure_console_logger_handler(**self.console_params)]

        # Suppress FileExistsError because it is raised when self.heartbeat_path is None, which means heartbeat is blacklisted
        with suppress(FileExistsError):
            logger_handlers.append(self.configure_heartbeat_logger_handler(**self.heartbeat_params))

        logging.basicConfig(handlers=logger_handlers, level=logging.DEBUG)

        self.debug('Logging Logging has been initialized!')

    @staticmethod
    def configure_console_logger_handler(level='INFO', fmt=None, datefmt=None, style='%', **kwargs):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        fmt = fmt or '<%(asctime)s> %(message)s'
        formatter = logging.Formatter(fmt=fmt, datefmt=datefmt, style=style)
        console_handler.setFormatter(formatter)
        return console_handler

    def configure_heartbeat_logger_handler(self, level='DEBUG', fmt=None, datefmt=None, style='%', **kwargs):
        # fmt = '<%(asctime)s> %(levelname)-8s - %(lineno)4d %(module)20s .%(funcName)10s - %(message)s'
        if self.heartbeat_path is None:
            raise FileExistsError

        file_handler = logging.FileHandler(self.heartbeat_path, mode='w')
        file_handler.setLevel(level)

        fmt = fmt or '<%(asctime)s> %(levelname)-8s - %(message)s'
        formatter = logging.Formatter(fmt=fmt, datefmt=datefmt, style=style)
        file_handler.setFormatter(formatter)
        return file_handler

    ##################################################
    # Placeholder Methods:
    ##################################################
    def log(self, content, **kwargs):
        pass

    def debug(self, content, **kwargs):
        pass

    def warn(self, content, **kwargs):
        pass

    ##################################################
    # Logging-Logging Methods:
    ##################################################
    def _logging_log(self, content, previous_frame=None, add_time=False, **kwargs):
        if self.add_frame is True:
            previous_frame = inspect.currentframe().f_back if previous_frame is None else previous_frame
            try:
                frame_source = format_frame_source(previous_frame)
            finally:
                del previous_frame
            content = frame_source + ' - ' + content

        content = add_time_to_content(content, add_time=add_time)
        logging.info(content)

    def _logging_debug(self, content, previous_frame=None, add_time=False, **kwargs):
        if self.add_frame is True:
            previous_frame = inspect.currentframe().f_back if previous_frame is None else previous_frame
            try:
                frame_source = format_frame_source(previous_frame)
            finally:
                del previous_frame
            content = frame_source + ' - ' + content

        content = add_time_to_content(content, add_time=add_time)
        logging.debug(content)

    def _logging_warn(self, content, **kwargs):
        if self.add_frame is True:
            previous_frame = inspect.currentframe().f_back
            try:
                frame_source = format_frame_source(previous_frame)
            finally:
                del previous_frame
            content = frame_source + ' - ' + content

        logging.warning(content)

    ##################################################
    # Standard Logging Methods:
    ##################################################
    # def _standard_log(self, content, add_time=False, **kwargs):
    #     content = add_time_to_content(content, add_time=add_time)
    #     print(content)
    #
    #     if self.heartbeat_path is not None:
    #         self.heartbeat(content)

    # def _standard_debug(self, content, add_time=False, **kwargs):
    #     content = add_time_to_content(content, add_time=add_time)
    #     print(content)
    #
    #     if self.heartbeat_path is not None:
    #         self.heartbeat(content)

    # def _standard_warn(self, content, **kwargs):
    #     warnings.warn(content)
    #
    #     if self.heartbeat_path is not None:
    #         self.heartbeat(content)


class Color():
    BLUE = '\033[94m'
    CYAN = '\033[36m'
    GREEN = '\033[32m'
    MAGENTA = '\033[35m'
    RED = '\033[31m'
    STOP = '\033[0m'


class OptimizationReporter():
    def __init__(self, parameter_names, verbose=1, show_experiment_id=True):
        """A MixIn class for reporting the results of hyperparameter optimization rounds

        Parameters
        ----------
        parameter_names: List
            The names of the hyperparameters being evaluated and optimized
        verbose: Integer in [0, 1, 2], default=1
            If 0, all but critical logging is silenced. If 1, normal logging is performed. If 2, detailed logging is performed
        show_experiment_id: Boolean or 'partial', default=True
            If True, the experiment_id will be printed in each result row. If False, it will not. If string 'partial', the first
            eight characters of each experiment_id will be printed in each row"""
        self.parameter_names = parameter_names
        self.verbose = verbose
        self.show_experiment_id = show_experiment_id

        self.end = ' | '
        self.y_max = None
        self.x_max = None
        self.iteration = 0

        self.start_time = datetime.now()
        self.last_round = datetime.now()

        self.sizes = [max(len(_), 7) for _ in self.parameter_names]
        self.sorted_indexes = sorted(
            range(len(self.parameter_names)),
            key=self.parameter_names.__getitem__
        )

    def print_saved_results_header(self):
        """Print a header signifying that saved Experiment results are being read"""
        header = F'{Color.RED}Saved Result Files{Color.STOP}'
        line = (Color.RED + '_' * (29 + sum([_ + 5 for _ in self.sizes])) + Color.STOP)
        self.print_header(header, line)

    # def print_saved_result(self):
    #     """Print a row containing the results of a saved Experiment read from a file"""
    #     pass

    def print_random_points_header(self):
        """Print a header signifying that random point evaluation rounds are starting"""
        header = F'{Color.RED}Random Point Evaluation{Color.STOP}'
        line = (Color.RED + '_' * (29 + sum([_ + 5 for _ in self.sizes])) + Color.STOP)
        self.print_header(header, line)

    def print_optimization_header(self):
        """Print a header signifying that Optimization rounds are starting"""
        header = F'{Color.RED}Hyperparameter Optimization{Color.STOP}'
        line = (Color.RED + '_' * (29 + sum([_ + 5 for _ in self.sizes])) + Color.STOP)
        self.print_header(header, line)

    def print_header(self, header, line):
        """Utility to perform actual printing of headers given formatted inputs"""
        print(header)
        print(line)

        self.print_column_name('Step', 5)  # TODO: Change to 'Iteration', 'Epoch', 'Round', '#', ...
        self.print_column_name('Time', 6)
        self.print_column_name('Value', 10)

        for index in self.sorted_indexes:
            self.print_column_name(self.parameter_names[index], self.sizes[index] + 2)
        print('')

    def print_column_name(self, value, size):
        print('{0:>{1}}'.format(value, size), end=self.end)

    def print_result(self, hyperparameters, evaluation):
        """Print a row containing the results of an Experiment just executed

        Parameters
        ----------
        hyperparameters: List
            List of hyperparameter values in the same order as :attr:`parameter_names`
        evaluation: Float
            An evaluation of the performance of `hyperparameters`"""
        if not self.verbose:
            return
        print('{:>5d}'.format(self.iteration), end=self.end)

        minutes, seconds = divmod((datetime.now() - self.last_round).total_seconds(), 60)
        print('{:>02d}m{:>02d}s'.format(int(minutes), int(seconds)), end=self.end)

        # TODO: Add printing experiment_id to each row (or first ~8 characters)

        if self.y_max is None or self.y_max < evaluation:
            self.y_max, self.x_max = evaluation, hyperparameters
            self.print_target_value(evaluation, pre=Color.MAGENTA, post=Color.STOP)
            self.print_input_values(hyperparameters, pre=Color.GREEN, post=Color.STOP)
        else:
            self.print_target_value(evaluation)
            self.print_input_values(hyperparameters)

        print('')
        self.last_round = datetime.now()
        self.iteration += 1

    def print_target_value(self, value, pre='', post=''):
        content = pre + '{: >10.5f}'.format(value) + post
        print(content, end=self.end)

    def print_input_values(self, values, pre='', post=''):
        for index in self.sorted_indexes:
            if isinstance(values[index], float):
                content = '{0: >{1}.{2}f}'.format(
                    values[index],
                    self.sizes[index] + 2,
                    min(self.sizes[index] - 3, 6 - 2)
                )
            else:
                content = '{0: >{1}}'.format(
                    values[index],
                    self.sizes[index] + 2,
                )
            print(pre + content + post, end=self.end)

    def reset_timer(self):
        self.start_time = datetime.now()
        self.last_round = datetime.now()

    def print_summary(self):
        # TODO: Finish this
        if not self.verbose:
            return
        pass


def format_frame_source(previous_frame, **kwargs):
    source = inspect.getframeinfo(previous_frame)
    source_script, source_line_no, source_func, source_class = source[0], source[1], source[2], None

    with suppress(AttributeError, KeyError):
        source_class = type(previous_frame.f_locals['self']).__name__

    return stringify_frame_source(source_script, source_line_no, source_func, source_class, **kwargs)


def stringify_frame_source(src_file, src_line_no, src_func, src_class, add_line_no=True, max_line_no_size=4, total_max_size=80):
    source_content = ''

    if add_line_no is True:
        # Left-align line_no to size: max_line_no_size
        source_content += '{0:<{1}}'.format(src_line_no, max_line_no_size)
        source_content += ' - '

    script_name = os.path.splitext(os.path.basename(src_file))[0]

    if src_class is not None:
        source_content += '{}.{}.{}()'.format(script_name, src_class, src_func)
    else:
        source_content += '{}.{}()'.format(script_name, src_func)

    source_content = '{0:<{1}}'.format(source_content, total_max_size)

    return source_content


def add_time_to_content(content, add_time=False):
    add_content = ''
    add_time = now_time() if add_time is True else add_time
    add_content += 'Time: {}'.format(add_time) if add_time else ''

    #################### Combine Original Content with New Content ####################
    if add_content != '':
        content += '   ' if ((content != '') and (not content.endswith(' '))) else ''
        content += add_content

    return content


def format_fold_run(fold=None, run=None, mode='concise'):
    content = ''
    valid_fold, valid_run = isinstance(fold, int), isinstance(run, int)

    if mode == 'verbose':
        content += format('Fold' if valid_fold else '')
        content += format('/' if valid_fold and valid_run else '')
        content += format('Run' if valid_run else '')
        content += format(': ' if valid_fold or valid_run else '')
        content += format(fold if valid_fold else '')
        content += format('/' if valid_fold and valid_run else '')
        content += format(run if valid_run else '')
    elif mode == 'concise':
        content += format('F' if valid_fold else '')
        content += format(fold if valid_fold else '')
        content += format('/' if valid_fold and valid_run else '')
        content += format('R' if valid_run else '')
        content += format(run if valid_run else '')
    else:
        raise ValueError('Received invalid mode value: "{}". Expected mode string'.format(mode))

    return content


# def format_evaluation_results(results, separator='   ', float_format='{:.5f}'):
#     if isinstance(results, list):
#         raise TypeError('Sorry, I can\'t deal with results of type list. Please send me an OrderedDict, instead')
#
#     content = []
#
#     for data_type, values in results.items():
#         if values is None: continue
#
#         data_type = 'OOF' if data_type == 'oof' else data_type
#         data_type = 'Holdout' if data_type == 'holdout' else data_type
#         data_type = 'In-Fold' if data_type == 'in_fold' else data_type
#
#         for metric_id, metric_value in values.items():
#             try:
#                 formatted_value = float_format.format(metric_value)
#             except ValueError:
#                 formatted_value = '{}'.format(metric_value)
#
#             content.append('{} {}: {}'.format(data_type, metric_id, formatted_value))
#
#     content = separator.join(content)
#     return content


def format_evaluation_results(results, separator='  |  ', float_format='{:.5f}'):
    if isinstance(results, list):
        raise TypeError('Sorry, I can\'t deal with results of type list. Please send me an OrderedDict, instead')

    content = []

    for data_type, values in results.items():
        if values is None: continue

        data_type = 'OOF' if data_type == 'oof' else data_type
        data_type = 'Holdout' if data_type == 'holdout' else data_type
        data_type = 'In-Fold' if data_type == 'in_fold' else data_type

        metric_entry = '{}('.format(data_type)
        metric_entry_vals = []

        for metric_id, metric_value in values.items():
            try:
                formatted_value = float_format.format(metric_value)
            except ValueError:
                formatted_value = '{}'.format(metric_value)

            metric_entry_vals.append('{}={}'.format(metric_id, formatted_value))

        metric_entry += (', '.join(metric_entry_vals) + ')')
        content.append(metric_entry)

    content = separator.join(content)
    return content


ADVANCED_FIT_LOGGING_DISPLAY_LAYOUT = [
    {
        "column_name": "General",
        "sub_columns_names": [
            ["fold", "Fold"],
            ["run", "Run"],
            ["seed", "Seed"],
            ["step", "Step"],
            ["start_time", "Start Time"],
            ["end_time", "End Time"],
            ["time_elapsed", "Time Elapsed"]
        ],
        "sub_column_min_sizes": [10, 10, 10, 20, 12, 12, 12]
    },
    # Will need to alter default "Score" sub-columns according to what metrics are actually being used
    {
        "column_name": "OOF Scores",
        "sub_columns_names": [
            ["oof_f1", "F1"],
            ["oof_roc_auc", "ROC_AUC"]
        ]
    },
    # Check that Holdout dataset is in use before adding "Holdout Scores" column
    {
        "column_name": "Holdout Scores",
        "sub_columns_names": [
            ["holdout_f1", "F1"],
            ["holdout_roc_auc", "ROC_AUC"]
        ]
    },
    {
        "column_name": "Losses",
        "sub_columns_names": [
            ["train_loss", "Train"],
            ["validation_loss", "Validation"]
        ]
    },
]


class AdvancedDisplayLayout(object):
    def __init__(self):
        pass


class AdvancedFitLogging(object):
    def __init__(self, display_layout=None, ):
        self.display_layout = display_layout or ADVANCED_FIT_LOGGING_DISPLAY_LAYOUT

    def validate_parameters(self):
        pass

    def validate_display_layout(self):
        pass


def log(*contents, blocks=True, pad='#', size=80, sep='   ', pre_embed='', post_embed='', log_pad=1, float_format='{:.5f}'):
    """Logs provided content according to formatting specifications

    Parameters
    ----------
    contents: Any number of arguments, whose types are handled
        The values to be joined by sep to form the message
    blocks: Boolean, default=True
        If True, print a block of size-many pad characters before and after the message content
    pad: String, default='#'
        The character used to create the pre/post blocks
    size: Integer, default=80
        The number of characters that pre_block and post_block should span
    sep: String, default='   '
        The string used to join contents' arguments to form the message
    pre_embed: String or None (empty string), default=''
        Content to be embedded in the center of pre_block, if truthy and blocks=True
    post_embed: String or None (empty string), default=''
        Content to be embedded in the center of post_block, if truthy and blocks=True
    log_pad: Integer, default=1
        Number of times to print given pad before the message content
    float_format: Valid string to format float, default='{:.5f}'
        Format all floats in contents by using this. If no formatting is desired, set float_format='{}'

    Notes
    -----
    - If the length of the final message line is greater than size, size will be set to its length
    - If the length of either block is greater than size after including its embedding, the block will consist of:
        - ((pad * 5) + sep + embedding + sep + (pad * 5))
    - All lines are forced to have even-numbered lengths by adding a space if they are odd

    Examples
    --------
    >>> from hyperparameter_hunter.utils.general_utils import now_time
    >>> from inspect import stack
    >>> c = ['OOF RMSLE: ', 0.5923750, 'HOLDOUT RMSLE: ', 0.4875906098498, 'TIME: ', now_time()]
    >>> log(*c)
    ################################################################################
    #   OOF RMSLE: 0.38592   HOLDOUT_RMSLE: 0.48759   TIME: 22:08:43
    ################################################################################
    >>> log(*c, size=70, pre_embed=now_time())
    ############################   22:25:35   ############################
    #   OOF RMSLE: 0.38592   HOLDOUT_RMSLE: 0.48759   TIME: 22:25:35
    ######################################################################
    >>> log(*c, pre_embed=now_time(), post_embed=stack()[0][1])
    ########################################   22:08:43   ########################################
    #   OOF RMSLE: 0.38592   HOLDOUT_RMSLE: 0.48759   TIME: 22:08:43
    #########   /Users/Hunter/hyperparameter_hunter/hyperparameter_hunter/reporting.py   #########
    >>> log(*c, pre_embed=now_time(), post_embed=stack()[0][1].split('/')[-1])
    #################################   22:08:43   #################################
    #   OOF RMSLE: 0.38592   HOLDOUT_RMSLE: 0.48759   TIME: 22:08:43
    ###############################   reporting.py   ###############################
    >>> log(*c, pad='!', pre_embed=now_time(), post_embed=stack()[0][1].split('/')[-1])
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!   22:23:21   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !   OOF RMSLE: 0.38592   HOLDOUT_RMSLE: 0.48759   TIME: 22:23:21
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!   reporting.py   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    """

    #################### Build Message Content Line ####################
    message = ''
    message += (pad * log_pad)

    for i, val in enumerate(contents):
        if isinstance(val, str):
            if not bool(re.match(r'[\d ]', val[0])):
                message += sep  # If val[0] is not a number or a space, prepend sep
            message += val
        elif isinstance(val, float):
            message += '{}'.format(float_format).format(val)
        elif isinstance(value, Exception):
            message += '{}'.format(val.__repr__())
        else:
            try:
                message += '{}'.format(val)
            except Exception as _ex:
                message += ' ERROR: CONTENT AT INDEX={}... TYPE={}... EXCEPTION={}'.format(i, type(val), _ex.__repr__())

    message += sep

    #################### Print Message and Exit if Blocks is False ####################
    if blocks is False:
        print(message)
        exit()

    #################### Build Pre/Post Block Lines ####################
    pre_line = '{0}{1}{0}'.format(sep, pre_embed) if pre_embed else ''
    post_line = '{0}{1}{0}'.format(sep, post_embed) if post_embed else ''

    #################### Make All Line Lengths Even by Adding 1 if Odd ####################
    message, size, pre_line, post_line = to_even(message), to_even(size), to_even(pre_line), to_even(post_line)

    #################### Calculate Longest Line and Padding for Pre/Post Lines ####################
    max_len = max([len(message), len(pre_line), len(post_line), size])
    pre_chars, post_chars = (max_len - len(pre_line)), (max_len - len(post_line))

    if (max_len == len(pre_line)) or (max_len == len(post_line)):
        pre_chars, post_chars = (pre_chars + 10), (post_chars + 10)

    #################### Add Padding to Pre/Post Lines ####################
    pre_line = '{0}{1}{0}'.format((pad * (pre_chars // 2)), pre_line)
    post_line = '{0}{1}{0}'.format((pad * (post_chars // 2)), post_line)

    print('{}\n{}\n{}'.format(pre_line, message, post_line))


def warn(*contents, blocks=True, pad='!', size=80, sep='   ', pre_embed='', post_embed='', log_pad=1, float_format='{:.5f}'):
    log(
        *contents, blocks=blocks, pad=pad, size=size, sep=sep, pre_embed=pre_embed, post_embed=post_embed,
        log_pad=log_pad, float_format=float_format
    )


def run_log_examples():
    contents = ['OOF RMSLE: ', 0.385923758920757201, 'HOLDOUT_RMSLE: ', 0.4875906098329498035430, 'TIME: ', now_time()]

    log(*contents)
    print('\n\n\n')
    log(*contents, size=70, pre_embed=now_time())
    print('\n\n\n')
    log(*contents, pre_embed=now_time(), post_embed=inspect.stack()[0][1])
    print('\n\n\n')
    log(*contents, pre_embed=now_time(), post_embed=inspect.stack()[0][1].split('/')[-1])
    print('\n\n\n')
    warn(*contents, pre_embed=now_time(), post_embed=inspect.stack()[0][1].split('/')[-1])
    print('')


def execute():
    run_log_examples()


if __name__ == '__main__':
    execute()