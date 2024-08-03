#include <stdio.h>
#include <libavutil/avutil.h>
#include <libavformat/avformat.h>

int main() {
    int ret;
    AVFormatContext* fc = NULL;
    char filename[256];

    double x = 0;

    av_log_set_level(AV_LOG_QUIET);

    for (int i = 0; i < 1400; i++) {
        snprintf(filename, 256, "data/pronunciations/%d.mp3", i + 1);

        ret = avformat_open_input(&fc, filename, NULL, NULL);
        if (ret < -1) {
            fprintf(stderr, "oh no.");
            return -1;
        }
        ret = avformat_find_stream_info(fc, NULL);
        if (ret < -1) {
            fprintf(stderr, "oh no. (2)");
            return -1;
        }
        x += (double)fc->duration / AV_TIME_BASE;
        printf("%lf\n", x);
        avformat_close_input(&fc);
    }

}
