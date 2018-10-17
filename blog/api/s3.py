
import os, json, boto3, mimetypes
from blog.api.errors import bad_file_type

def make_s3_signature(file_name):

    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')

    s3 = boto3.client('s3')

    file_name = file_name.replace(' ', '_').lower()

    ext_type = file_name.split('.')[-1]

    if ext_type in set(['png', 'jpg', 'jpeg', 'gif']):

        mime_type = mimetypes.guess_type(file_name)[0]

        # save send back signature to store image in s3 bucket
        presigned_post = s3.generate_presigned_post(
            Bucket = S3_BUCKET_NAME,
            Key = file_name,
            Fields = {"acl": "public-read", "Content-Type": mime_type},
            Conditions = [
              {"acl": "public-read"},
              {"Content-Type": mime_type}
            ],
            ExpiresIn = 3600
        )

        return {
            'data': presigned_post,
            'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET_NAME, file_name)
          }

    return bad_file_type('file type unsupported')

        #image.save(basedir + '/static/pictures/' + file_name)
