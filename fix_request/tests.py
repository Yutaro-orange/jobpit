from django.test import TestCase, Client
from .models import AttendanceFixRequests
from datetime import datetime

# Create your tests here.
class AttendanceFixRequestTest(TestCase):
    fixtures = ['test_attendance_fix_records.json']
    def setUp(self):
        self.client = Client()
        self.client.login(
            username='testuser',
            password='samplesecret'
        )

    def test_not_exist_attendance_fix_request(self):
        '''
        attendancesにない打刻修正申請を行うためのテスト
        '''
        # 打刻修正のページを開く
        response = self.client.get('/fix_request/request')
        # ステータスコードが200であること
        self.assertEqual(response.status_code, 200)
        # contextの申請情報が存在しないこと
        self.assertEqual(len(response.context['fix_requests']), 0)

        # 2021/5/21の出勤打刻の修正を申請する
        response = self.client.post('/fix_request/request', {
            'push_date': '2021-05-03',
            'push_type': 'AT',
            'push_time': '9:30',
            'push_reason': 'テスト用'
        })
        # 登録されたデータを取得
        attendance_request = AttendanceFixRequests.objects.get(
            revision_time__date = datetime.strptime('2021-05-03', '%Y-%m-%d')
        )

        self.assertEqual(response.status_code, 200)
        # attendanceが空であること
        self.assertIsNone(attendance_request.attendance)

        # 打刻修正のページを開く
        response = self.client.get('/fix_request/request')
        self.assertEqual(response.status_code, 200)
        # contextの申請情報が1つ存在すること
        self.assertEqual(len(response.context['fix_requests']), 1)

    def test_exist_attendance_fix_attendanced_request(self):
        '''
        attendancesにある打刻修正申請を行うためのテスト
        '''
        # 打刻修正のページを開く
        response = self.client.get('/fix_request/request')
        # ステータスコードが200であること
        self.assertEqual(response.status_code, 200)
        # contextの申請情報が存在しないこと
        self.assertEqual(len(response.context['fix_requests']), 0)

        # 2021/5/21の退勤打刻の修正を申請する
        response = self.client.post('/fix_request/request', {
            'push_date': '2021-05-02',
            'push_type': 'LE',
            'push_time': '19:30',
            'push_reason': 'テスト用'
        })
        # 登録されたデータを取得
        attendance_request = AttendanceFixRequests.objects.get(
            revision_time__date = datetime.strptime('2021-05-02', '%Y-%m-%d')
        )

        self.assertEqual(response.status_code, 200)
        # 該当するattendancesのデータが登録されていること
        self.assertEqual(attendance_request.attendance.pk, 2)

        # 打刻修正のページを開く
        response = self.client.get('/fix_request/request')
        self.assertEqual(response.status_code, 200)
        # contextの申請情報が1つ存在すること
        self.assertEqual(len(response.context['fix_requests']), 1)
