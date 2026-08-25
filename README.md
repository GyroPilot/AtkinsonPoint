# Atkinsonpoint -- LISA Slide Show 1.0

A native slideshow tool for the Apple Lisa Office System.  It appears
on the LOS desktop as its own icon, opens into a full-window carousel,
and displays 680 x 300 one-bit pictures -- photographs dithered on a
modern computer and delivered to the Lisa over a serial line.  Click
or press a key to advance, or let it run itself at one of three
speeds.  Written in Lisa Pascal with the Workshop 3.0 toolchain; runs
under Lisa Office System 3.1 on real hardware.

## Why "Atkinsonpoint"

The name honors **Bill Atkinson** twice over, because this program
depends on him twice over.

Atkinson wrote **QuickDraw**, the graphics library at the heart of the
Lisa and, later, the Macintosh.  Every pixel this tool puts on the
screen -- the window, the menus, and the single CopyBits call that
blits each slide -- is drawn by his code, running where he wrote it.
QuickDraw on this machine is not a tribute or an emulation; it is the
original article, and this program is one more caller.

Atkinson also devised the **dithering algorithm that bears his name**:
a technique for turning grayscale photographs into pure black-and-white
images that still read as photographs.  Like Floyd-Steinberg dithering,
it diffuses each pixel's quantization error to its neighbors -- but
Atkinson's version deliberately spreads only three quarters of the
error (one eighth to each of six neighbors, discarding the rest).
Throwing part of the error away costs some shadow and highlight detail
but keeps the midtones crisp and airy, which is exactly right for a
1-bit screen viewed at arm's length.  It became the signature look of
early Macintosh imaging (MacPaint, HyperCard); on the Lisa's CRT it is,
if anything, even more at home.  Every slide this tool shows was
prepared with Atkinson dithering by default -- his algorithm makes the
pictures, his QuickDraw draws them.

And the name is a small pun on "PowerPoint," by way of **Teslerpoint**
(see Thanks): the Lisa was always meant to give presentations.

## Thanks

**Bill Atkinson** -- QuickDraw and the dither, as above.  This tool is
a two-part thank-you note.

**Tom Stepleton** -- his **Teslerpoint** proved that a Lisa makes a
fine slide carousel and inspired this program.  No Teslerpoint code is
used here (that program is bare-metal 68000 assembly; this one is
Pascal on the Office System), but the idea is his.  His lisabbs and
documentation work also underpin LISACom, this tool's companion.

**Alex Anderson-McLeod** (alexthecat123) -- his LOS Minesweeper is the
template every LOS desktop tool in this family is built from, and his
LOS Compilation Base image supplies the Workshop environment and
Apple's own ICONEDIT.  His LisaFPGA made nightly testing practical.

**The LisaList2 community**, **bitsavers.org**, and the **Computer
History Museum** (for the Lisa Office System source release).

Errors are mine, not theirs.

## Requirements

- Apple Lisa running Lisa Office System 3.x (developed on 3.1)
- On the modern side: any computer with Python 3 and Pillow
  (pip install pillow) to prepare pictures
- A way to move files onto the Lisa.  The natural partner is
  **LISACom**, this tool's sibling: YMODEM the pictures over a serial
  line.  Any method that lands exact binary files works.

## The picture format

Simple enough to memorize:

    680 x 300 pixels, 1 bit per pixel
    85 bytes per row, high bit leftmost, 1 = black
    no header, no padding: exactly 25,500 bytes

Files are named `1.PIX`, `2.PIX`, ... on the Lisa's boot volume and
play in catalog order (zero-pad past nine: `01.PIX` ... `10.PIX`,
because the catalog sorts alphabetically).  The format is also
described inside the tool itself: Version menu -> Making Pictures.

## Making pictures

`lisapix.py` (in this distribution) converts JPG/PNG to .PIX:

    python lisapix.py photo.jpg 1.PIX --fill --preview p1.png

- `--fill`    scale to cover and center-crop: fills the whole frame.
              Best for landscape photographs.
- `--window`  letterbox the whole image, uncropped.  Best for
              portraits, documents, and title cards.
- `--dither`  fs | atkinson | ordered | threshold  (default atkinson;
              threshold is best for text and line art)
- `--par`     pixel-aspect prescale, default 1.40 -- the Lisa's pixels
              are not square, and this keeps circles circular
- `--preview` writes a PNG of exactly what the Lisa will show

Every output is exactly 25,500 bytes; anything else is an error.

Send pictures to the Lisa as BINARY files (in LISACom: Receive via
YMODEM, RETURN to accept the sender's name).  If the slideshow is
already open, choose **Look Again for Pictures** from the Show menu.

## Using the slideshow

Open the LISA Slide Show icon.  The first picture appears; then:

- **Click or almost any key** -- next slide
- **B** -- previous slide
- **A** -- toggle auto-advance
- **Speed menu** -- Slow / Medium / Fast auto-advance
- **Show menu** -- Look Again for Pictures (rescan the disk)
- **Version menu** -- About, and the built-in picture-making guide

Set Aside or Save & Put Away from File/Print, as with any LOS tool.

## Installing

The distribution floppy carries the tool **and a starter show of nine
pictures**, so it demonstrates itself out of the box.

**The tool:** insert the floppy, **Duplicate** (not drag -- dragging
is a move) the LISA Slide Show icon onto your ProFile window, and open
it.  Five files travel with the icon; LOS manages them.  Never drag a
tool's icon to the Wastebasket -- LOS deletes the tool's whole hidden
file set with it.

**The pictures:** the nine .PIX files (1.PIX ... 9.PIX) are ordinary
files, copied with the Workshop's File Manager rather than the
desktop.  They belong on THE SAME VOLUME THE TOOL WAS INSTALLED ON --
the slideshow looks for its pictures next to itself.  Boot the
Workshop, then:

    F                          (File-Mgr)
    C                          (Copy)
    from:  -LOWER-=.PIX
    to:    =.PIX               (or -VOLUME-=.PIX if the tool lives on
                                a volume other than the boot disk)

-LOWER- is the Lisa's floppy drive; the = wildcard copies all nine in
one command.  Boot the Office System, open LISA Slide Show, and if it
was already open choose Look Again for Pictures from the Show menu.
The floppy can then be put away.

## Building from source

Six sources: SLD-MAIN.TEXT, SLD-GLOBALS.TEXT, SLD-ALERTS.TEXT,
SLD-COMP.TEXT, SLD-LINK.TEXT, SLD-MAKE.TEXT.  Format each with
fmt_text.py before sending (Workshop .TEXT files are paged, bare-CR),
place them in the SLD/ slots, then from the Workshop: R <SLD/MAKE.
Menus are matched by position: MAIN, GLOBALS and ALERTS change in
lockstep.

Two hard-won 68000/QuickDraw lessons are baked into this code, left
here for the next person:

1. **A bitmap's rowBytes must be even.**  680/8 = 85 is odd; the fix
   strides 86 bytes per row in memory while the file stays 85.  Odd
   rowBytes puts alternate rows at odd addresses, and the 68000
   address-errors on the first word access.
2. **Pad heap-allocated image buffers.**  The allocator can place a
   buffer at the very base of an MMU data segment, and QuickDraw's
   blitter reads a couple of bytes below baseAddr on non-aligned
   transfers -- straight into unmapped space.  Eight bytes of padding
   ends a Level 7 bus error that took two weeks to corner.

## History

Atkinsonpoint began in August 2026 as part of a project to write new
native software for the Lisa Office System, alongside LISACom (the
serial/BBS tool that delivers its pictures).  It was parked for two
weeks on a mysterious bus error, then revived when a diagnostic build
painted every input to CopyBits on screen and the crash confessed in
two photographs -- the two lessons above.  Everything in this README
was verified on a Lisa 2/10 and a LisaFPGA.

Bugs and ideas: post to LisaList2.
# AtkinsonPoint
