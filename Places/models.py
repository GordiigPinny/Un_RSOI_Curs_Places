from django.db import models
from django.db.models import CheckConstraint, Q, Avg
from Places.managers import PlaceImagesManager, PlacesManager, RatingsManager, AcceptsManager


class Place(models.Model):
    """
    Модель места
    """
    name = models.CharField(max_length=512, null=False, blank=False)
    latitude = models.FloatField(null=False, blank=False)
    longitude = models.FloatField(null=False, blank=False)
    address = models.CharField(max_length=512, null=False, blank=False)
    created_by = models.PositiveIntegerField(null=False, blank=False)
    created_dt = models.DateTimeField(auto_now_add=True)
    deleted_flg = models.BooleanField(default=False)

    objects = PlacesManager()

    @property
    def rating(self) -> float:
        rating = self.ratings.filter(deleted_flg=False).aggregate(Avg('rating')).values()
        rating = list(rating)
        return 0 if len(rating) == 0 else rating[0]

    @property
    def accepts_cnt(self):
        return self.accepts.count()

    @property
    def accept_type(self):
        cnt = self.accepts_cnt
        if cnt < 50:
            return 'Непроверенное место'
        elif 50 <= cnt < 100:
            return 'Слабо проверенное место'
        elif 100 <= cnt < 200:
            return 'Проверенное многими место'
        else:
            return 'Проверенное место'

    def soft_delete(self):
        self.deleted_flg = True
        self.save(update_fields=['deleted_flg'])

    def __str__(self):
        return f'Place {self.name}'

    class Meta:
        constraints = [
            CheckConstraint(check=Q(latitude__gte=55.515174) & Q(latitude__lte=56.106229), name='lat_msk_constraint'),
            CheckConstraint(check=Q(longitude__gte=36.994695) & Q(longitude__lte=37.956703), name='long_msk_constraint'),
        ]


class Accept(models.Model):
    """
    Модель для одобрения выложенного места
    """
    created_by = models.PositiveIntegerField(null=False, blank=False)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='accepts')
    created_dt = models.DateTimeField(auto_now_add=True)
    deleted_flg = models.BooleanField(default=False)

    objects = AcceptsManager()

    def soft_delete(self):
        self.deleted_flg = True
        self.save(update_fields=['deleted_flg'])

    def __str__(self):
        return f'Accept({self.id}) by {self.created_by}, on place {self.place.id}'


class Rating(models.Model):
    """
    Модель рейтинга, который юзер дает месту
    """
    created_by = models.PositiveIntegerField(null=False, blank=False)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveIntegerField(null=False, blank=False)
    created_dt = models.DateTimeField(auto_now_add=True)
    updated_dt = models.DateTimeField(auto_now_add=True)
    deleted_flg = models.BooleanField(default=False)

    objects = RatingsManager()

    def soft_delete(self):
        self.deleted_flg = True
        self.save(update_fields=['deleted_flg'])

    def __str__(self):
        return f'Rating({self.id}) {self.rating} on place {self.place}'

    class Meta:
        constraints = [
            CheckConstraint(check=Q(rating__gte=0) & Q(rating__lte=5), name='rating_number_constraint'),
        ]


class PlaceImage(models.Model):
    """
    Модель картинки места
    """
    created_by = models.PositiveIntegerField(null=False, blank=False)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='images')
    pic_id = models.PositiveIntegerField(null=False)
    created_dt = models.DateTimeField(auto_now_add=True)
    deleted_flg = models.BooleanField(default=False)

    objects = PlaceImagesManager()

    def soft_delete(self):
        self.deleted_flg = True
        self.save(update_fields=['deleted_flg'])

    def __str__(self):
        return f'Image({self.id}) of place {self.place}'
