# A part of NonVisual Desktop Access (NVDA)
# Copyright (C) 2020-2021 NV Access Limited, Leonard de Ruijter
# This file may be used under the terms of the GNU General Public License, version 2 or later.
# For more details see: https://www.gnu.org/licenses/gpl-2.0.html

"""Logic for NVDA + Google Chrome tests
"""

import os
from robot.libraries.BuiltIn import BuiltIn
# imported methods start with underscore (_) so they don't get imported into robot files as keywords
from SystemTestSpy import (
	_getLib,
)

# Imported for type information
from ChromeLib import ChromeLib as _ChromeLib
from AssertsLib import AssertsLib as _AssertsLib
import NvdaLib as _NvdaLib

_builtIn: BuiltIn = BuiltIn()
_chrome: _ChromeLib = _getLib("ChromeLib")
_asserts: _AssertsLib = _getLib("AssertsLib")


#: Double space is used to separate semantics in speech output this typically
# adds a slight pause to the synthesizer.
SPEECH_SEP = "  "
SPEECH_CALL_SEP = '\n'


ARIAExamplesDir = os.path.join(
	_NvdaLib._locations.repoRoot, "include", "w3c-aria-practices", "examples"
)


def checkbox_labelled_by_inner_element():
	_chrome.prepareChrome(
		r"""
			<div tabindex="0" role="checkbox" aria-labelledby="inner-label">
				<div style="display:inline" id="inner-label">
					Simulate evil cat
				</div>
			</div>
		"""
	)
	actualSpeech = _chrome.getSpeechAfterTab()
	_asserts.strings_match(
		actualSpeech,
		# The name for the element is also in it's content, the name is spoken twice:
		# "Simulate evil cat  Simulate evil cat  check box  not checked"
		# Instead this should be spoken as:
		"Simulate evil cat  check box  not checked"
	)


def test_mark_aria_details():
	_chrome.prepareChrome(
		"""
		<div>
			<p>The word <mark aria-details="cat-details">cat</mark> has a comment tied to it.</p>
			<div id="cat-details" role="comment">
				Cats go woof BTW<br>&mdash;Jonathon Commentor
				<div role="comment">
				No they don't<br>&mdash;Zara
				</div>
				<div role="form">
				<textarea cols="80" placeholder="Add reply..."></textarea>
				<input type="submit">
				</div>
			</div>
		</div>
		"""
	)
	actualSpeech = _chrome.getSpeechAfterKey('downArrow')
	_asserts.strings_match(
		actualSpeech,
		"The word  highlighted  has details  cat  out of highlighted  has a comment tied to it."
	)
	# this word has no details attached
	actualSpeech = _chrome.getSpeechAfterKey("control+rightArrow")
	_asserts.strings_match(
		actualSpeech,
		"word"
	)
	# check that there is no summary reported
	actualSpeech = _chrome.getSpeechAfterKey("NVDA+\\")
	_asserts.strings_match(
		actualSpeech,
		"No additional details"
	)
	# this word has details attached to it
	actualSpeech = _chrome.getSpeechAfterKey("control+rightArrow")
	_asserts.strings_match(
		actualSpeech,
		"highlighted  has details  cat  out of highlighted"
	)
	# read the details summary
	actualSpeech = _chrome.getSpeechAfterKey("NVDA+\\")
	_asserts.strings_match(
		actualSpeech,
		"Cats go woof BTW  Jonathon Commentor No they don't  Zara Submit"
	)


def announce_list_item_when_moving_by_word_or_character():
	_chrome.prepareChrome(
		r"""
			<div contenteditable="true">
				<p>Before list</p>
				<ul style="list-style-type:none">
					<li>small cat</li>
					<li>big dog</li>
				</ul>
			</div>
		"""
	)
	# Force focus mode
	actualSpeech = _chrome.getSpeechAfterKey("NVDA+space")
	_asserts.strings_match(
		actualSpeech,
		"Focus mode"
	)
	# Tab into the contenteditable
	actualSpeech = _chrome.getSpeechAfterKey("tab")
	_asserts.strings_match(
		actualSpeech,
		"section  multi line  editable  Before list"
	)
	# Ensure that moving into a list by line, "list item" is not reported.
	actualSpeech = _chrome.getSpeechAfterKey("downArrow")
	_asserts.strings_match(
		actualSpeech,
		"list  small cat"
	)
	# Ensure that when moving by word (control+rightArrow)
	# within the list item, "list item" is not announced.
	actualSpeech = _chrome.getSpeechAfterKey("control+rightArrow")
	_asserts.strings_match(
		actualSpeech,
		"cat"
	)
	# Ensure that when moving by character (rightArrow)
	# within the list item, "list item" is not announced.
	actualSpeech = _chrome.getSpeechAfterKey("rightArrow")
	_asserts.strings_match(
		actualSpeech,
		"a"
	)
	# move to the end of the line (and therefore the list item)
	actualSpeech = _chrome.getSpeechAfterKey("end")
	_asserts.strings_match(
		actualSpeech,
		"blank"
	)
	# Ensure that when moving by character (rightArrow)
	# onto the next list item, "list item" is reported.
	actualSpeech = _chrome.getSpeechAfterKey("rightArrow")
	_asserts.strings_match(
		actualSpeech,
		SPEECH_CALL_SEP.join([
			"list item  level 1",
			"b"
		])
	)
	# Ensure that when moving by character (leftArrow)
	# onto the previous list item, "list item" is reported.
	# Note this places us on the end-of-line insertion point of the previous list item.
	actualSpeech = _chrome.getSpeechAfterKey("leftArrow")
	_asserts.strings_match(
		actualSpeech,
		"list item  level 1"
	)
	# Ensure that when moving by word (control+rightArrow)
	# onto the next list item, "list item" is reported.
	actualSpeech = _chrome.getSpeechAfterKey("control+rightArrow")
	_asserts.strings_match(
		actualSpeech,
		"list item  level 1  big"
	)
	# Ensure that when moving by word (control+leftArrow)
	# onto the previous list item, "list item" is reported.
	# Note this places us on the end-of-line insertion point of the previous list item.
	actualSpeech = _chrome.getSpeechAfterKey("control+leftArrow")
	_asserts.strings_match(
		actualSpeech,
		"list item  level 1"
	)


def test_i7562():
	""" List should not be announced on every line of a ul in a contenteditable """
	_chrome.prepareChrome(
		r"""
			<div contenteditable="true">
				<p>before</p>
				<ul>
					<li>frogs</li>
					<li>birds</li>
				</ul>
				<p>after</p>
			</div>
		"""
	)
	# Force focus mode
	actualSpeech = _chrome.getSpeechAfterKey("NVDA+space")
	_asserts.strings_match(
		actualSpeech,
		"Focus mode"
	)
	# Tab into the contenteditable
	actualSpeech = _chrome.getSpeechAfterKey("tab")
	_asserts.strings_match(
		actualSpeech,
		"section  multi line  editable  before"
	)
	# DownArow into the list. 'list' should be announced when entering.
	actualSpeech = _chrome.getSpeechAfterKey("downArrow")
	_asserts.strings_match(
		actualSpeech,
		"list  bullet  frogs"
	)
	# DownArrow to the second list item. 'list' should not be announced.
	actualSpeech = _chrome.getSpeechAfterKey("downArrow")
	_asserts.strings_match(
		actualSpeech,
		"bullet  birds"
	)
	# DownArrow out of the list. 'out of list' should be announced.
	actualSpeech = _chrome.getSpeechAfterKey("downArrow")
	_asserts.strings_match(
		actualSpeech,
		"out of list  after",
	)


def test_pr11606():
	"""
	Announce the correct line when placed at the end of a link at the end of a list item in a contenteditable
	"""
	_chrome.prepareChrome(
		r"""
			<div contenteditable="true">
				<ul>
					<li><a href="#">A</a> <a href="#">B</a></li>
					<li>C D</li>
				</ul>
			</div>
		"""
	)
	# Force focus mode
	actualSpeech = _chrome.getSpeechAfterKey("NVDA+space")
	_asserts.strings_match(
		actualSpeech,
		"Focus mode"
	)
	# Tab into the contenteditable
	actualSpeech = _chrome.getSpeechAfterKey("tab")
	_asserts.strings_match(
		actualSpeech,
		"section  multi line  editable  list  bullet  link  A    link  B"
	)
	# move past the end of the first link.
	# This should not be affected due to pr #11606.
	actualSpeech = _chrome.getSpeechAfterKey("rightArrow")
	_asserts.strings_match(
		actualSpeech,
		SPEECH_CALL_SEP.join([
			"out of link",
			"space"
		])
	)
	# Move to the end of the line (which is also the end of the second link)
	# Before pr #11606 this would have announced the bullet on the next line.
	actualSpeech = _chrome.getSpeechAfterKey("end")
	_asserts.strings_match(
		actualSpeech,
		"link"
	)
	# Read the current line.
	# Before pr #11606 the next line ("C D")  would have been read.
	actualSpeech = _chrome.getSpeechAfterKey("NVDA+upArrow")
	_asserts.strings_match(
		actualSpeech,
		"bullet  link  A    link  B"
	)


def test_ariaTreeGrid_browseMode():
	"""
	Ensure that ARIA treegrids are accessible as a standard table in browse mode.
	"""
	testFile = os.path.join(ARIAExamplesDir, "treegrid", "treegrid-1.html")
	_chrome.prepareChrome(
		f"""
			<iframe src="{testFile}"></iframe>
		"""
	)
	# Jump to the first heading in the iframe.
	actualSpeech = _chrome.getSpeechAfterKey("h")
	_asserts.strings_match(
		actualSpeech,
		"frame  main landmark  Treegrid Email Inbox Example  heading  level 1"
	)
	# Tab to the first link.
	# This ensures that focus is totally within the iframe
	# so as to not cause focus to hit the iframe's document
	# when entering focus mode on the treegrid later.
	actualSpeech = _chrome.getSpeechAfterKey("tab")
	_asserts.strings_match(
		actualSpeech,
		"issue 790.  link"
	)
	# Jump to the ARIA treegrid with the next table quicknav command.
	# The browse mode caret will be inside the table on the caption before the first row.
	actualSpeech = _chrome.getSpeechAfterKey("t")
	_asserts.strings_match(
		actualSpeech,
		"Inbox  table  clickable  with 5 rows and 3 columns  Inbox"
	)
	# Move past the caption onto row 1 with downArrow
	actualSpeech = _chrome.getSpeechAfterKey("downArrow")
	_asserts.strings_match(
		actualSpeech,
		"row 1  column 1  Subject"
	)
	# Navigate to row 2 column 1 with NVDA table navigation command
	actualSpeech = _chrome.getSpeechAfterKey("control+alt+downArrow")
	_asserts.strings_match(
		actualSpeech,
		"expanded  level 1  row 2  Treegrids are awesome"
	)
	# Press enter to activate NVDA focus mode and focus the current row
	actualSpeech = _chrome.getSpeechAfterKey("enter")
	_asserts.strings_match(
		actualSpeech,
		SPEECH_CALL_SEP.join([
			# focus mode turns on
			"Focus mode",
			# Focus enters the ARIA treegrid (table)
			"Inbox  table",
			# Focus lands on row 2
			"level 1  Treegrids are awesome Want to learn how to use them? aaron at thegoogle dot rocks  expanded",
		])
	)


def ARIAInvalid_spellingAndGrammar():
	"""
	Tests ARIA invalid values of "spelling", "grammar" and "spelling, grammar".
	Please note that although IAccessible2 allows multiple values for invalid,
	multiple values to aria-invalid is not yet standard.
	And even if it were, they would be separated by space, not comma
thus the html for this test would need to change,
	but the expected output shouldn't need to.
	"""
	_chrome.prepareChrome(
		r"""
			<p>Big <span aria-invalid="spelling">caat</span> meos</p>
			<p>Small <span aria-invalid="grammar">a dog</span> woofs</p>
			<p>Fat <span aria-invalid="grammar, spelling">a ffrog</span> crokes</p>
		"""
	)
	actualSpeech = _chrome.getSpeechAfterKey("downArrow")
	_asserts.strings_match(
		actualSpeech,
		"Big  spelling error  caat  meos"
	)
	actualSpeech = _chrome.getSpeechAfterKey("downArrow")
	_asserts.strings_match(
		actualSpeech,
		"Small  grammar error  a dog  woofs"
	)
	actualSpeech = _chrome.getSpeechAfterKey("downArrow")
	_asserts.strings_match(
		actualSpeech,
		"Fat  spelling error  grammar error  a ffrog  crokes"
	)


def test_ariaCheckbox_browseMode():
	"""
	Navigate to an unchecked checkbox in reading mode.
	"""
	testFile = os.path.join(ARIAExamplesDir, "checkbox", "checkbox-1", "checkbox-1.html")
	_chrome.prepareChrome(
		f"""
			<iframe src="{testFile}"></iframe>
		"""
	)
	# Jump to the first heading in the iframe.
	actualSpeech = _chrome.getSpeechAfterKey("h")
	_asserts.strings_match(
		actualSpeech,
		"frame  main landmark  Checkbox Example (Two State)  heading  level 1"
	)
	# Navigate to the checkbox.
	actualSpeech = _chrome.getSpeechAfterKey("x")
	_asserts.strings_match(
		actualSpeech,
		"Sandwich Condiments  grouping  list  with 4 items  Lettuce  check box  not checked"
	)


def test_i12147():
	"""
	New focus target should be announced if the triggering element is removed when activated.
	"""
	_chrome.prepareChrome(
		f"""
			<div>
			  <button id='trigger0'>trigger 0</button>
			  <h4 id='target0' tabindex='-1'>target 0</h4>
			</div>
			<script>
				let trigger0 = document.querySelector('#trigger0');
				trigger0.addEventListener('click', e => {{
				  let focusTarget = document.querySelector('#target0');
				  trigger0.remove();
				  focusTarget.focus();
				}})
			</script>
		"""
	)
	# Jump to the first button (the trigger)
	actualSpeech = _chrome.getSpeechAfterKey("tab")
	_asserts.strings_match(
		actualSpeech,
		"trigger 0  button"
	)
	# Activate the button, we should hear the new focus target.
	actualSpeech = _chrome.getSpeechAfterKey("enter")
	_asserts.strings_match(
		actualSpeech,
		"target 0  heading  level 4"
	)


def test_tableInStyleDisplayTable():
	"""
	Chrome treats nodes with `style="display: table"` as tables.
	When a HTML style table is positioned in such a node, NVDA was previously unable to announce
	table row and column count as well as provide table navigation for the inner table.
	"""
	_chrome.prepareChrome(
		"""
			<p>Paragraph</p>
			<div style="display:table">
				<table>
					<thead>
						<tr>
							<th>First heading</th>
							<th>Second heading</th>
						</tr>
					</thead>
					<tbody>
						<tr>
							<td>First content cell</td>
							<td>Second content cell</td>
						</tr>
					</tbody>
				</table>
			</div>
		"""
	)
	# Jump to the table
	actualSpeech = _chrome.getSpeechAfterKey("t")
	_asserts.strings_match(
		actualSpeech,
		"table  with 2 rows and 2 columns  row 1  column 1  First heading"
	)
	nextActualSpeech = _chrome.getSpeechAfterKey("control+alt+downArrow")
	_asserts.strings_match(
		nextActualSpeech,
		"row 2  First content cell"
	)


def test_ariaRoleDescription_focus():
	"""
	NVDA should report the custom role of an object on focus.
	"""
	_chrome.prepareChrome(
		"""
		<button aria-roledescription="pizza">Cheese</button><br />
		<button aria-roledescription="pizza">Meat</button>
		"""
	)
	actualSpeech = _chrome.getSpeechAfterKey("tab")
	_asserts.strings_match(
		actualSpeech,
		"Cheese  pizza"
	)
	# Force focus mode
	actualSpeech = _chrome.getSpeechAfterKey("NVDA+space")
	_asserts.strings_match(
		actualSpeech,
		"Focus mode"
	)
	actualSpeech = _chrome.getSpeechAfterKey("tab")
	_asserts.strings_match(
		actualSpeech,
		"Meat  pizza"
	)


def test_ariaRoleDescription_inline_browseMode():
	"""
	NVDA should report the custom role for inline elements in browse mode.
	"""
	_chrome.prepareChrome(
		"""
		<p>Start
		<img aria-roledescription="drawing" alt="Our logo" src="https://www.nvaccess.org/images/logo.png" />
		End</p>
		"""
	)
	# When reading the entire line,
	# entering the custom role should be reported,
	# but not exiting
	actualSpeech = _chrome.getSpeechAfterKey("downArrow")
	_asserts.strings_match(
		actualSpeech,
		"Start  drawing  Our logo  End"
	)
	# When reading the line by word,
	# Both entering and exiting the custom role should be reported.
	actualSpeech = _chrome.getSpeechAfterKey("control+rightArrow")
	_asserts.strings_match(
		actualSpeech,
		"drawing  Our"
	)
	actualSpeech = _chrome.getSpeechAfterKey("control+rightArrow")
	_asserts.strings_match(
		actualSpeech,
		"logo  out of drawing"
	)
	actualSpeech = _chrome.getSpeechAfterKey("control+rightArrow")
	_asserts.strings_match(
		actualSpeech,
		"End"
	)


def test_ariaRoleDescription_block_browseMode():
	"""
	NVDA should report the custom role at start and end for block elements in browse mode.
	"""
	_chrome.prepareChrome(
		"""
		<aside aria-roledescription="warning">
		<p>Wet paint!</p>
		<p>Please be careful.</p>
		</aside>
		<p>End</p>
		"""
	)
	# when reading the page by line,
	# both entering and exiting the custom role should be reported.
	actualSpeech = _chrome.getSpeechAfterKey("downArrow")
	_asserts.strings_match(
		actualSpeech,
		"warning  Wet paint!"
	)
	actualSpeech = _chrome.getSpeechAfterKey("downArrow")
	_asserts.strings_match(
		actualSpeech,
		"Please be careful."
	)
	actualSpeech = _chrome.getSpeechAfterKey("downArrow")
	_asserts.strings_match(
		actualSpeech,
		"out of warning  End"
	)


def test_ariaRoleDescription_inline_contentEditable():
	"""
	NVDA should report the custom role for inline elements in content editables.
	"""
	_chrome.prepareChrome(
		"""
		<div contenteditable="true">
		<p>Top line</p>
		<p>Start
		<img aria-roledescription="drawing" alt="Our logo" src="https://www.nvaccess.org/images/logo.png" />
		End</p>
		</div>
		"""
	)
	# Force focus mode
	actualSpeech = _chrome.getSpeechAfterKey("NVDA+space")
	_asserts.strings_match(
		actualSpeech,
		"Focus mode"
	)
	actualSpeech = _chrome.getSpeechAfterKey("tab")
	_asserts.strings_match(
		actualSpeech,
		"section  multi line  editable  Top line"
	)
	# When reading the entire line,
	# entering the custom role should be reported,
	# but not exiting
	actualSpeech = _chrome.getSpeechAfterKey("downArrow")
	_asserts.strings_match(
		actualSpeech,
		"Start  drawing  Our logo    End"
	)
	# When reading the line by word,
	# Both entering and exiting the custom role should be reported.
	actualSpeech = _chrome.getSpeechAfterKey("control+rightArrow")
	_asserts.strings_match(
		actualSpeech,
		"drawing  Our logo    out of drawing"
	)
	actualSpeech = _chrome.getSpeechAfterKey("control+rightArrow")
	_asserts.strings_match(
		actualSpeech,
		"End"
	)


def test_ariaRoleDescription_block_contentEditable():
	"""
	NVDA should report the custom role at start and end for block elements in content editables.
	"""
	_chrome.prepareChrome(
		"""
		<div contenteditable="true">
		<p>Top line</p>
		<aside aria-roledescription="warning">
		<p>Wet paint!</p>
		<p>Please be careful.</p>
		</aside>
		<p>End</p>
		</div>
		"""
	)
	# Force focus mode
	actualSpeech = _chrome.getSpeechAfterKey("NVDA+space")
	_asserts.strings_match(
		actualSpeech,
		"Focus mode"
	)
	actualSpeech = _chrome.getSpeechAfterKey("tab")
	_asserts.strings_match(
		actualSpeech,
		"section  multi line  editable  Top line"
	)
	# when reading the page by line,
	# both entering and exiting the custom role should be reported.
	actualSpeech = _chrome.getSpeechAfterKey("downArrow")
	_asserts.strings_match(
		actualSpeech,
		"warning  Wet paint!"
	)
	actualSpeech = _chrome.getSpeechAfterKey("downArrow")
	_asserts.strings_match(
		actualSpeech,
		"Please be careful."
	)
	actualSpeech = _chrome.getSpeechAfterKey("downArrow")
	_asserts.strings_match(
		actualSpeech,
		"out of warning  End"
	)


def _getAriaDescriptionSample() -> str:
	annotation = "User nearby, Aaron"
	linkDescription = "opens in a new tab"
	# link title should be read in focus
	linkTitle = "conduct a search"
	linkContents = "to google's"
	return f"""
			<div>
				<div
					contenteditable=""
					spellcheck="false"
					role="textbox"
					aria-multiline="true"
				><p>This is a line with no annotation</p>
				<p><span
						aria-description="{annotation}"
					>Here is a sentence that is being edited by someone else.</span>
					<b>Multiple can edit this.</b></p>
				<p>An element with a role, follow <a
					href="www.google.com"
					aria-description="{linkDescription}"
					>{linkContents}</a
				> website</p>
				<p>Testing the title attribute, <a
					href="www.google.com"
					title="{linkTitle}"
					>{linkContents}</a
				> website</p>
				</div>
			</div>
		"""


def test_ariaDescription_focusMode():
	""" Ensure aria description is read in focus mode.
	Settings which may affect this:
	- speech.reportObjectDescriptions default:True
	- annotations.reportAriaDescription default:True
	"""
	_chrome.prepareChrome(_getAriaDescriptionSample())
	# Focus the contenteditable and automatically switch to focus mode (due to contenteditable)
	actualSpeech = _chrome.getSpeechAfterKey("tab")
	_asserts.strings_match(
		actualSpeech,
		"edit  multi line  This is a line with no annotation\nFocus mode"
	)

	actualSpeech = _chrome.getSpeechAfterKey('downArrow')
	# description-from hasn't reached Chrome stable yet.
	# reporting aria-description only supported in Chrome canary 92.0.4479.0+
	_asserts.strings_match(
		actualSpeech,
		SPEECH_SEP.join([
			"User nearby, Aaron",  # annotation
			"Here is a sentence that is being edited by someone else.",  # span text
			"Multiple can edit this.",  # bold paragraph text
		])
	)

	actualSpeech = _chrome.getSpeechAfterKey('downArrow')
	# description-from hasn't reached Chrome stable yet.
	# reporting aria-description only supported in Chrome canary 92.0.4479.0+
	_asserts.strings_match(
		actualSpeech,
		SPEECH_SEP.join([  # two space separator
			"An element with a role, follow",  # paragraph text
			"link",  # link role
			"opens in a new tab",  # link description
			"to google's",  # link contents (name)
			"website"  # paragraph text
		])
	)

	# 'title' attribute for link ("conduct a search") should not be announced.
	# too often title is used without screen reader users in mind, and is overly verbose.
	actualSpeech = _chrome.getSpeechAfterKey('downArrow')
	_asserts.strings_match(
		actualSpeech,
		SPEECH_SEP.join([
			"Testing the title attribute,",  # paragraph text
			"link",  # link role
			"to google's",  # link contents (name)
			"website"  # paragraph text
		])
	)


def test_ariaDescription_browseMode():
	""" Ensure aria description is read in browse mode.
	Settings which may affect this:
	- speech.reportObjectDescriptions default:True
	- annotations.reportAriaDescription default:True
	"""
	_chrome.prepareChrome(_getAriaDescriptionSample())
	actualSpeech = _chrome.getSpeechAfterKey("downArrow")
	_asserts.strings_match(
		actualSpeech,
		"edit  multi line  This is a line with no annotation"
	)

	actualSpeech = _chrome.getSpeechAfterKey('downArrow')
	# description-from hasn't reached Chrome stable yet.
	# reporting aria-description only supported in Chrome canary 92.0.4479.0+
	_asserts.strings_match(
		actualSpeech,
		SPEECH_SEP.join([
			"User nearby, Aaron",  # annotation
			"Here is a sentence that is being edited by someone else.",  # span text
			"Multiple can edit this.",  # bold paragraph text
		])
	)

	actualSpeech = _chrome.getSpeechAfterKey('downArrow')
	# description-from hasn't reached Chrome stable yet.
	# reporting aria-description only supported in Chrome canary 92.0.4479.0+
	_asserts.strings_match(
		actualSpeech,
		SPEECH_SEP.join([  # two space separator
			"An element with a role, follow",  # paragraph text
			"link",  # link role
			"opens in a new tab",  # link description
			"to google's",  # link contents (name)
			"website"  # paragraph text
		])
	)

	# 'title' attribute for link ("conduct a search") should not be announced.
	# too often title is used without screen reader users in mind, and is overly verbose.
	actualSpeech = _chrome.getSpeechAfterKey('downArrow')
	_asserts.strings_match(
		actualSpeech,
		SPEECH_SEP.join([
			"Testing the title attribute,",  # paragraph text
			"link",  # link role
			"to google's",  # link contents (name)
			"website"  # paragraph text
		])
	)


def test_ariaDescription_sayAll():
	""" Ensure aria description is read by say all.
	# Historically, description was not announced at all in browse mode with arrow navigation,
	# annotations are now a special case.

	Settings which may affect this:
	- speech.reportObjectDescriptions default:True
	- annotations.reportAriaDescription default:True
	"""
	_chrome.prepareChrome(_getAriaDescriptionSample())
	actualSpeech = _chrome.getSpeechAfterKey("NVDA+downArrow")

	# Reporting aria-description only supported in:
	# - Chrome 92.0.4479.0+
	_asserts.strings_match(
		actualSpeech,
		SPEECH_CALL_SEP.join([
			"Test page load complete",
			"edit  multi line  This is a line with no annotation",
			SPEECH_SEP.join([
				"User nearby, Aaron",  # annotation
				"Here is a sentence that is being edited by someone else.",  # span text
				"Multiple can edit this.",  # bold paragraph text
			]),
			SPEECH_SEP.join([  # two space separator
				"An element with a role, follow",  # paragraph text
				"link",  # link role
				"opens in a new tab",  # link description
				"to google's",  # link contents (name)
				"website",  # paragraph text
			]),
			# 'title' attribute for link ("conduct a search") should not be announced.
			# too often title is used without screen reader users in mind, and is overly verbose.
			SPEECH_SEP.join([
				"Testing the title attribute,",  # paragraph text
				"link",  # link role
				# note description missing when sourced from title attribute
				"to google's",  # link contents (name)
				"website",  # paragraph text
				"out of edit"
			]),
			"After Test Case Marker"
		])
	)


def test_i10840():
	"""
	The name of table header cells should only be conveyed once when navigating directly to them in browse mode
	Chrome self-references a header cell as its own header, which used to cause the name to be announced twice
	"""
	_chrome.prepareChrome(
		f"""
			<table>
				<thead>
					<tr>
						<th>Month</th>
						<th>items</th>
					</tr>
				</thead>
				<tbody>
					<tr>
						<td>January</td>
						<td>100</td>
					</tr>
					<tr>
						<td>February</td>
						<td>80</td>
					</tr>
				</tbody>
				<tfoot>
					<tr>
						<td>Sum</td>
						<td>180</td>
					</tr>
				</tfoot>
				</table>
		"""
	)
	# Jump to the table
	actualSpeech = _chrome.getSpeechAfterKey("t")
	_asserts.strings_match(
		actualSpeech,
		"table  with 4 rows and 2 columns  row 1  column 1  Month"
	)
	nextActualSpeech = _chrome.getSpeechAfterKey("control+alt+rightArrow")
	_asserts.strings_match(
		nextActualSpeech,
		"column 2  items"
	)


def test_mark_browse():
	_chrome.prepareChrome(
		"""
		<div>
			<p>The word <mark>Kangaroo</mark> is important.</p>
		</div>
		"""
	)
	actualSpeech = _chrome.getSpeechAfterKey('downArrow')
	_asserts.strings_match(
		actualSpeech,
		"The word  highlighted  Kangaroo  out of highlighted  is important."
	)
	# Test moving by word
	actualSpeech = _chrome.getSpeechAfterKey("numpad6")
	_asserts.strings_match(
		actualSpeech,
		"word"
	)
	actualSpeech = _chrome.getSpeechAfterKey("numpad6")
	_asserts.strings_match(
		actualSpeech,
		"highlighted  Kangaroo  out of highlighted"
	)


def test_mark_focus():
	_chrome.prepareChrome(
		"""
		<div>
			<p>The word <mark><a href="#">Kangaroo</a></mark> is important.</p>
		</div>
		"""
	)

	# Force focus mode
	actualSpeech = _chrome.getSpeechAfterKey("NVDA+space")
	_asserts.strings_match(
		actualSpeech,
		"Focus mode"
	)

	actualSpeech = _chrome.getSpeechAfterKey('tab')
	_asserts.strings_match(
		actualSpeech,
		"highlighted\nKangaroo  link"
	)


def test_preventDuplicateSpeechFromDescription_browse_tab():
	"""
	When description matches name/content, it should not be spoken.
	This prevents duplicate speech.
	Settings which may affect this:
	- speech.reportObjectDescriptions default:True
	"""
	spy = _NvdaLib.getSpyLib()
	REPORT_OBJ_DESC_KEY = ["presentation", "reportObjectDescriptions"]
	spy.set_configValue(REPORT_OBJ_DESC_KEY, True)

	_chrome.prepareChrome(
		"""
		<a href="#" title="apple" style="display:block">apple</a>
		<a href="#" title="banana" aria-label="banana" style="display:block">contents</a>
		"""
	)
	# Read in browse
	actualSpeech = _chrome.getSpeechAfterKey('tab')
	_asserts.strings_match(
		actualSpeech,
		"apple  link"
	)
	actualSpeech = _chrome.getSpeechAfterKey('tab')
	_asserts.strings_match(
		actualSpeech,
		"banana  link"
	)


def preventDuplicateSpeechFromDescription_focus():
	"""
	When description matches name/content, it should not be spoken.
	This prevents duplicate speech.
	Settings which may affect this:
	- speech.reportObjectDescriptions default:True
	"""
	spy = _NvdaLib.getSpyLib()
	REPORT_OBJ_DESC_KEY = ["presentation", "reportObjectDescriptions"]
	spy.set_configValue(REPORT_OBJ_DESC_KEY, True)

	_chrome.prepareChrome(
		"""
		<a href="#" title="apple" style="display:block">apple</a>
		<a href="#" title="banana" aria-label="banana" style="display:block">contents</a>
		"""
	)
	# Force focus mode
	actualSpeech = _chrome.getSpeechAfterKey("NVDA+space")
	_asserts.strings_match(
		actualSpeech,
		"Focus mode"
	)
	actualSpeech = _chrome.getSpeechAfterKey('tab')
	_asserts.strings_match(
		actualSpeech,
		"apple  link"
	)
	actualSpeech = _chrome.getSpeechAfterKey('tab')
	_asserts.strings_match(
		actualSpeech,
		"banana  link"
	)
