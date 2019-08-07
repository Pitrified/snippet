from PIL import ImageTk, Image
import exifread

class PhotoInfo:
    def __init__(self, photo, thumb_size=50):
        self.photo = photo
        #  self.thumb_size = (thumb_size, thumb_size)
        self.thumb_size = thumb_size

        #  self.define_useful_tags()
        #  self.get_metadata()

        self.load_thumbnail()

    def define_useful_tags(self):
        """Populate set of useful tags"""
        self.useful_tags = set(
            [
                "JPEGThumbnail",
                "TIFFThumbnail",
                "Filename",
                #  'EXIF MakerNote',
                # 'Image Tag 0x000B',
                # 'Image ImageDescription',
                "Image Make",
                "Image Model",
                "Image Orientation",
                # 'Image XResolution',
                # 'Image YResolution',
                # 'Image ResolutionUnit',
                "Image Software",
                "Image DateTime",
                # 'Image YCbCrPositioning',
                # 'Image ExifOffset',
                # 'Image PrintIM',
                # 'Image Padding',
                "GPS GPSLatitudeRef",
                "GPS GPSLatitude",
                "GPS GPSLongitudeRef",
                "GPS GPSLongitude",
                # 'GPS GPSAltitudeRef',
                # 'GPS GPSTimeStamp',
                # 'GPS GPSSatellites',
                # 'GPS GPSImgDirectionRef',
                # 'GPS GPSMapDatum',
                # 'GPS GPSDate',
                # 'Image GPSInfo',
                # 'Thumbnail Compression',
                # 'Thumbnail XResolution',
                # 'Thumbnail YResolution',
                # 'Thumbnail ResolutionUnit',
                # 'Thumbnail JPEGInterchangeFormat',
                # 'Thumbnail JPEGInterchangeFormatLength',
                "EXIF ExposureTime",
                "EXIF FNumber",
                "EXIF ExposureProgram",
                "EXIF ISOSpeedRatings",
                # 'EXIF ExifVersion',
                "EXIF DateTimeOriginal",
                "EXIF DateTimeDigitized",
                # 'EXIF ComponentsConfiguration',
                # 'EXIF CompressedBitsPerPixel',
                # 'EXIF BrightnessValue',
                "EXIF ExposureBiasValue",
                # 'EXIF MaxApertureValue',
                # 'EXIF MeteringMode',
                # 'EXIF LightSource',
                "EXIF Flash",
                "EXIF FocalLength",
                # 'EXIF UserComment',
                # 'EXIF FlashPixVersion',
                # 'EXIF ColorSpace',
                "EXIF ExifImageWidth",
                "EXIF ExifImageLength",
                # 'Interoperability InteroperabilityVersion',
                # 'EXIF InteroperabilityOffset',
                # 'EXIF FileSource',
                # 'EXIF SceneType',
                # 'EXIF CustomRendered',
                "EXIF ExposureMode",
                "EXIF WhiteBalance",
                "EXIF DigitalZoomRatio",
                "EXIF FocalLengthIn35mmFilm",
            ]
        )

    def get_metadata(self):
        """Load metadata for Photo, according to useful list"""
        with open(self.photo, "rb") as f:
            tags = exifread.process_file(f)

        #  print(f'type tags {type(tags)}')
        #  print(f'for {self.photo} len tags {len(tags.keys())}')

        #  for tag in tags.keys():
        #  if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
        #  print(f'Key: {tag}, value: {tags[tag]}')

    def load_thumbnail(self):
        """resize the pic"""
        #  img = Image.open(self.photo)
        self.thumb = Image.open(self.photo)
        self.thumb.thumbnail((self.thumb_size, self.thumb_size), Image.BICUBIC)
        #  self.thumb.thumbnail(self.thumb_size, Image.LANCZOS)



